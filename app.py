from datetime import datetime

from fastapi import FastAPI, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional
from fastapi.middleware.cors import CORSMiddleware
import subprocess
import json
from services.product_service import ProductService
from services.website_service import WebsiteService
from utils.send_notification import notify

app = FastAPI()

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update this with your allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Models
class WebsiteCreate(BaseModel):
    display_name: str
    url: str
    scraper_name: str
    search_url: str


class ProductCreate(BaseModel):
    name: str
    website_name: str
    url: str
    search_name: str
    price: str
    in_stock: bool
    image_url: str


class WebsiteResponse(BaseModel):
    id: int
    display_name: str
    url: str
    scraper_name: str
    search_url: str


class ProductPriceResponse(BaseModel):
    id: int
    price: str
    timestamp: datetime

    class Config:
        # Ensure datetime is serialized in ISO format
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ProductResponse(BaseModel):
    id: int
    name: str
    url: str
    active: bool
    in_stock: bool
    last_scraped: Optional[datetime]  # Optional because it can be None
    created_at: Optional[datetime]  # Optional because it can be None
    website: Optional[WebsiteResponse]  # Optional because it can be None
    prices: List[ProductPriceResponse]  # List of prices

    class Config:
        # Ensure datetime is serialized in ISO format
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ScrapeRequest(BaseModel):
    product_name: str


def handle_scrape(products, scraper_name):
    product_service = ProductService()

    for product in products:
        product_service.add_product(
            product.get('name'),
            scraper_name,
            product.get('search_name'),
            product.get('url'),
            product.get('price'),
            product.get('in_stock'),
            product.get('image_url')
        )

def test():
    product_service = ProductService()
    products = [product.serialize() for product in product_service.get_all_products()]

    for product in products:
        print(product)
        prod = product_service.get_product_by_display_name(product.get("name"))
        assert prod is not None

def handle_products_rescrape(products, scraper_name):
    product_service = ProductService()

    for product in products:
        existing_product = product_service.get_product_by_display_name_and_url(product.get('name'), product.get('url'))
        if existing_product is not None:
            handle_rescrape_for_single_product(product, existing_product.flat_serialize())
        else:
            #handle adding new product
            handle_scrape([product], scraper_name)

def handle_rescrape_for_single_product(product, existing_product):
    product_service = ProductService()

    update_data = {"last_scraped": datetime.utcnow()}

    if existing_product.get('in_stock') != product.get('in_stock'):
        update_data["in_stock"] = product.get('in_stock')

    product_service.update_product(existing_product.get('id'), update_data)

    if existing_product.get('price') != product_service.parse_price(product.get('price')):
        product_service.add_price(
            existing_product.get('id'),
            product.get('price'),
        )
        notify(f"Price change: New price for {product.get('name')} is {product_service.parse_price(product.get('price'))}. Old price: {existing_product.get('price')}", force=True)

# Background Task
def run_scraper(scraper_name: str, product_name, scrape_type: str):
    command = [
        'python', './scrapers/main.py',
        scraper_name,
        product_name,
        "scrape"
    ]

    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        print(result.stdout)  # Replace this with actual processing logic
        parsed_output = json.loads(result.stdout)
        # Process the parsed output (e.g., save to database)

        if scrape_type == "scrape":
            handle_scrape(parsed_output, scraper_name)
        elif scrape_type == "rescrape":
            handle_products_rescrape(parsed_output, scraper_name)


    except subprocess.CalledProcessError as e:
        print(e.output)
    except json.JSONDecodeError as e:
        print(f"JSON decoding error: {e}")

    notify(f"Scraper {scraper_name} finished scraping")


# Routes
@app.get("/")
def read_root():
    return {"message": "Hello World!"}


@app.post("/websites", response_model=WebsiteResponse)
def add_website(website: WebsiteCreate):
    website_service = WebsiteService()
    website = website_service.add_website(
        website.display_name,
        website.url,
        website.scraper_name,
        website.search_url
    )
    return website.serialize()


@app.get("/websites", response_model=List[WebsiteResponse])
def get_websites():
    website_service = WebsiteService()
    websites = website_service.get_all_websites()
    return [website.serialize() for website in websites]


@app.post("/products", response_model=ProductResponse)
def add_product(product: ProductCreate):
    product_service = ProductService()
    product = product_service.add_product(
        product.name,
        product.website_name,
        product.url,
        product.search_name,
        product.price,
        product.in_stock,
        product.image_url
    )
    return product.serialize()


@app.get("/products")
def get_products():
    product_service = ProductService()
    products = product_service.get_all_products()
    serialized_products = [product.serialize() for product in products]

    return JSONResponse(content={"products": serialized_products})


@app.post("/scrape")
async def scrape(request: ScrapeRequest, background_tasks: BackgroundTasks):
    product_name = request.product_name
    product_service = ProductService()
    products = product_service.get_product_by_name(product_name)

    website_service = WebsiteService()
    scraped_websites = website_service.get_websites_by_search_name(product_name)

    scraped_website_ids = {website.id for website in scraped_websites}

    websites = website_service.get_all_websites()

    websites = [website for website in websites if website.id not in scraped_website_ids]

    if len(websites) == 0:
        return JSONResponse(content={"products": [product.serialize() for product in products]})

    # Queue the scraping tasks
    for website in websites:
        background_tasks.add_task(run_scraper, website.serialize().get('scraper_name'), product_name, "scrape")

    return {"job": "queued"}


@app.post("/rescrape")
async def rescrape(background_tasks: BackgroundTasks):
    product_service = ProductService()
    # Get all unique search names
    product_search_names = [product[0] for product in product_service.get_unique_search_products()]

    website_service = WebsiteService()
    websites = [website.serialize() for website in website_service.get_all_websites()]

    for website in websites:
        if not website.get('enabled'):
            print(f"Skipping {website.get('url')}")
            continue

        for product_name in product_search_names:
            print(f"Processing {product_name} with {website.get('url')}")
            background_tasks.add_task(run_scraper, website.get('scraper_name'), product_name, "rescrape")

    return {"job": "queued"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app:app", host="0.0.0.0", port=3001, log_level="info", reload=True)
