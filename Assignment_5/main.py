

from fastapi import FastAPI

app = FastAPI()


# 1st Question : Add 3 More Products

# Products List
products = [
    {"id": 1, "name": "Smartphone", "price": 15000, "category": "Electronics", "in_stock": True},
    {"id": 2, "name": "Headphones", "price": 2000, "category": "Electronics", "in_stock": True},
    {"id": 3, "name": "Coffee Maker", "price": 3500, "category": "Home Appliances", "in_stock": False},
    {"id": 4, "name": "Office Chair", "price": 7000, "category": "Furniture", "in_stock": True},

    # Newly Added Products
    {"id": 5, "name": "Laptop Stand", "price": 1200, "category": "Accessories", "in_stock": True},
    {"id": 6, "name": "Mechanical Keyboard", "price": 4500, "category": "Accessories", "in_stock": True},
    {"id": 7, "name": "Webcam", "price": 3000, "category": "Electronics", "in_stock": False},
    {"id": 8, "name": "Wireless Mouse", "price": 800, "category": "Electronics", "in_stock": True}
]


# Endpoint to Get All Products
@app.get("/products")
def get_products():
    return {
        "products": products,
        "total": len(products)
    }
    
    
    
# 2nd Question : Add a Category Filter Endpoint 


@app.get("/products/category/{category_name}")
def get_products_by_category(category_name: str):
    filtered_products = [
        product for product in products
        if product["category"].lower() == category_name.lower()
    ]

    if not filtered_products:
        return {"error": "No products found in this category"}

    return {
        "category": category_name,
        "products": filtered_products,
        "total": len(filtered_products)
    }
    
    
# 3rd Question : Show only In-Stock Products

@app.get("/products/instock")
def get_instock_products():
    in_stock_products = [
        product for product in products
        if product["in_stock"] == True
    ]

    return {
        "in_stock_products": in_stock_products,
        "count": len(in_stock_products)
    }
    
    
# 4th Question : Build a store Info Endpoint

@app.get("/store/summary")
def get_store_summary():
    total_products = len(products)

    in_stock_count = len([
        product for product in products
        if product["in_stock"] == True
    ])

    out_of_stock_count = total_products - in_stock_count

    categories = list(set([
        product["category"] for product in products
    ]))

    return {
        "store_name": "My E-commerce Store",
        "total_products": total_products,
        "in_stock": in_stock_count,
        "out_of_stock": out_of_stock_count,
        "categories": categories
    }
    
    
# 5th Question : Search Products by name


@app.get("/products/search/{keyword}")
def search_products(keyword: str):
    matched_products = []
    for product in products:
        if keyword.lower() in product["name"].lower():
            matched_products.append(product)
            
    if len(matched_products) == 0:
        return {"message": "No products matched your search"}

    return {
        "matched_products": matched_products,
        "total_matches": len(matched_products)
    }
    
    
# Bonus : Cheapest Product


@app.get("/products/deals")
def get_product_deals():
    if not products:
        return {"message": "No products available"}

    cheapest_product = min(products, key=lambda product: product["price"])
    expensive_product = max(products, key=lambda product: product["price"])

    return {
        "best_deal": cheapest_product,
        "premium_pick": expensive_product
    }
    
    
    



from pydantic import BaseModel, Field
from typing import Optional
from typing import List 

from fastapi import FastAPI

app = FastAPI()


# Question 1 : Filter Products by Minimum Price

products = [
    {"id" : 1,"name": "Wireless Mouse", "category": "electronics", "price": 499, "in_stock" : True},
    {"id" : 2,"name": "USB Hub", "category": "electronics", "price": 799, "in_stock" : True},
    {"id" : 2,"name": "Notebook", "category": "stationery", "price": 50, "in_stock" : False},
    {"id" : 2,"name": "Pen Set", "category": "Stationery", "price": 49, "in_stock" : True}
]

feedback = []


@app.get("/products/filter")
def filter_products(category: str = None, min_price: int = None, max_price: int = None):
    result = products

    if category:
        result = [p for p in result if p["category"] == category]

    if min_price:
        result = [p for p in result if p["price"] >= min_price]

    if max_price:
        result = [p for p in result if p["price"] <= max_price]

    return result


# Q2 : Get Only the Price of a Product


@app.get("/products/{product_id}/price")
def get_product_price(product_id: int):
    for product in products:
        if product["id"] == product_id:
            return {
                "name": product["name"],
                "price": product["price"]
            }
    
    return {"error": "Product not found"}

# Q3 :

class CustomerFeedback(BaseModel):
    customer_name: str = Field(..., min_length=2)
    product_id: int = Field(..., gt=0)
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = Field(None, max_length=300)
    
@app.post("/feedback")
def submit_feedback(data: CustomerFeedback):
    feedback.append(data.dict())

    return {
        "message": "Feedback submitted successfully",
        "feedback": data,
        "total_feedback": len(feedback)
}
    
# Q4 :


@app.get("/products/summary")
def product_summary():
    total_products = len(products)

    in_stock_count = len([p for p in products if p["in_stock"]])
    out_of_stock_count = len([p for p in products if not p["in_stock"]])

    most_expensive = max(products, key=lambda x: x["price"])
    cheapest = min(products, key=lambda x: x["price"])

    categories = list(set([p["category"] for p in products]))

    return {
        "total_products": total_products,
        "in_stock_count": in_stock_count,
        "out_of_stock_count": out_of_stock_count,
        "most_expensive": {
            "name": most_expensive["name"],
            "price": most_expensive["price"]
        },
        "cheapest": {
            "name": cheapest["name"],
            "price": cheapest["price"]
        },
        "categories": categories
    }
    
    
# Q5 :

class OrderItem(BaseModel):
    product_id: int = Field(..., gt=0)
    quantity: int = Field(..., ge=1, le=50)
    
    
class BulkOrder(BaseModel):
    company_name: str = Field(..., min_length=2)
    contact_email: str = Field(..., min_length=5)
    items: List[OrderItem] = Field(..., min_items=1)
    
@app.post("/orders/bulk")
def place_bulk_order(order: BulkOrder):

    confirmed = []
    failed = []
    grand_total = 0

    for item in order.items:

        product = next((p for p in products if p["id"] == item.product_id), None)

        if not product:
            failed.append({
                "product_id": item.product_id,
                "reason": "Product not found"
            })
            continue

        if not product["in_stock"]:
            failed.append({
                "product_id": item.product_id,
                "reason": f"{product['name']} is out of stock"
            })
            continue

        subtotal = product["price"] * item.quantity
        grand_total += subtotal

        confirmed.append({
            "product": product["name"],
            "qty": item.quantity,
            "subtotal": subtotal
        })

    return {
        "company": order.company_name,
        "confirmed": confirmed,
        "failed": failed,
        "grand_total": grand_total
    }
    
    
# Bonus Point Question : 

orders = []

class Order(BaseModel):
    product_id: int = Field(..., gt=0)
    quantity: int = Field(..., ge=1)
    
    
@app.post("/orders")
def create_order(order: Order):
    new_order = order.dict()
    new_order["id"] = len(orders) + 1
    new_order["status"] = "pending"

    orders.append(new_order)

    return new_order

@app.get("/orders/{order_id}")
def get_order(order_id: int):
    for order in orders:
        if order["id"] == order_id:
            return order

    return {"error": "Order not found"}


@app.patch("/orders/{order_id}/confirm")
def confirm_order(order_id: int):

    for order in orders:
        if order["id"] == order_id:
            order["status"] = "confirmed"
            return order

    return {"error": "Order not found"}
    
    


from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List

app = FastAPI()

products = [
    {"id": 1, "name": "Wireless Mouse", "price": 499, "category": "Electronics", "in_stock": True},
    {"id": 2, "name": "Notebook", "price": 99, "category": "Stationery", "in_stock": True},
    {"id": 3, "name": "USB Hub", "price": 799, "category": "Electronics", "in_stock": False},
    {"id": 4, "name": "Pen Set", "price": 49, "category": "Stationery", "in_stock": True}
]


# Q1 : Add two new products using POST 
class Product(BaseModel):
    name: str
    price: int
    category: str
    in_stock: bool


@app.post("/products", status_code=201)
def add_product(product: Product):

    # Check duplicate product name
    for p in products:
        if p["name"].lower() == product.name.lower():
            raise HTTPException(status_code=400, detail="Product with this name already exists")
        
    new_id = max(p["id"] for p in products) + 1

    new_product = {
        "id": new_id,
        "name": product.name,
        "price": product.price,
        "category": product.category,
        "in_stock": product.in_stock
    }

    products.append(new_product)

    return {
        "message": "Product added",
        "product": new_product
    }
    
    
# Q2 : Restock the USB Hub Using PUT

@app.put("/products/{product_id}")
def update_product(product_id: int, price: Optional[int] = None, in_stock: Optional[bool] = None):

    for product in products:
        if product["id"] == product_id:

            if price is not None:
                product["price"] = price

            if in_stock is not None:
                product["in_stock"] = in_stock

            return {
                "message": "Product updated",
                "product": product
            }

    raise HTTPException(status_code=404, detail="Product not found")


# Q3 : Delete a Product and Handle Missing IDs

@app.delete("/products/{product_id}")
def delete_product(product_id: int):

    for product in products:
        if product["id"] == product_id:
            products.remove(product)
            return {"message": f"Product '{product['name']}' deleted"}

    raise HTTPException(status_code=404, detail="Product not found")


# Q4 : Build a Product Summary Dashboard

@app.get("/products")
def get_products():
    return {
        "products": products,
        "total": len(products)
    }
    

# Q5 : Build GET /products/audit — Inventory Summary

@app.get("/products/audit")
def products_audit():

    total_products = len(products)

    in_stock_products = [p for p in products if p["in_stock"]]
    in_stock_count = len(in_stock_products)

    out_of_stock_names = [p["name"] for p in products if not p["in_stock"]]

    total_stock_value = sum(p["price"] * 10 for p in in_stock_products)

    most_expensive = max(products, key=lambda x: x["price"])

    return {
        "total_products": total_products,
        "in_stock_count": in_stock_count,
        "out_of_stock_names": out_of_stock_names,
        "total_stock_value": total_stock_value,
        "most_expensive": {
            "name": most_expensive["name"],
            "price": most_expensive["price"]
        }
    }
    
    
# Bonus Question : Apply a Category-Wide Discount

@app.get("/products/{product_id}")
def get_product(product_id: int):
    @app.put("/products/discount")
    def apply_discount(category: str, discount_percent: int):

        if discount_percent < 1 or discount_percent > 99:
            raise HTTPException(status_code=400, detail="Discount must be between 1 and 99")

        updated_products = []

        for product in products:
            if product["category"].lower() == category.lower():

                new_price = int(product["price"] * (1 - discount_percent / 100))
                product["price"] = new_price

                updated_products.append({
                    "name": product["name"],
                    "new_price": new_price
                })

            if not updated_products:
                return {"message": f"No products found in category '{category}'"}

        return {
        "updated_count": len(updated_products),
        "updated_products": updated_products
        }




from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List

app = FastAPI()

# Question : 1 Add Items to the Cart

# Products list (with IDs)
products = [
    {"id": 1, "name": "Wireless Mouse", "price": 499, "category": "Electronics", "in_stock": True},
    {"id": 2, "name": "Notebook", "price": 99, "category": "Stationery", "in_stock": True},
    {"id": 3, "name": "USB Hub", "price": 799, "category": "Electronics", "in_stock": False},
    {"id": 4, "name": "Pen Set", "price": 49, "category": "Stationery", "in_stock": True}
]

# Order list
orders = []
# Cart list
cart = []


cart = []

@app.post("/cart/add")
def add_to_cart(product_id: int, quantity: int):

    product = next((p for p in products if p["id"] == product_id), None)

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    if not product["in_stock"]:
        raise HTTPException(status_code=400, detail="Product out of stock")

    # check if product already in cart
    for item in cart:
        if item["product_id"] == product_id:
            item["quantity"] += quantity
            subtotal = item["quantity"] * product["price"]

            return {
                "message": "Cart updated",
                "cart_item": {
                    "product_id": product_id,
                    "product_name": product["name"],
                    "quantity": item["quantity"],
                    "unit_price": product["price"],
                    "subtotal": subtotal
                }
            }

    subtotal = quantity * product["price"]

    cart_item = {
        "product_id": product_id,
        "product_name": product["name"],
        "quantity": quantity,
        "unit_price": product["price"]
    }

    cart.append(cart_item)

    return {
        "message": "Added to cart",
        "cart_item": {
            **cart_item,
            "subtotal": subtotal
        }
    }



@app.get("/cart")
def view_cart():

    item_count = len(cart)
    grand_total = sum(item["quantity"] * item["unit_price"] for item in cart)

    return {
        "items": cart,
        "item_count": item_count,
        "grand_total": grand_total
    }


@app.delete("/cart/remove/{product_id}")
def remove_from_cart(product_id: int):

    for item in cart:
        if item["product_id"] == product_id:
            cart.remove(item)
            return {"message": "Item removed from cart"}

    raise HTTPException(status_code=404, detail="Item not in cart")

class CheckoutRequest(BaseModel):
    customer_name: str
    delivery_address: str

@app.post("/cart/checkout")
def checkout(data: CheckoutRequest):
    
    if not cart:
        raise HTTPException(status_code=400, detail="Cart is empty")

    customer_name = data.customer_name
    delivery_address = data.delivery_address

    order = {
        "order_id": len(orders) + 1,
        "customer_name": customer_name,
        "delivery_address": delivery_address,
        "items": cart.copy(),
        "total_amount": sum(item["unit_price"] * item["quantity"] for item in cart)
    }

    orders.append(order)
    cart.clear()

    return {
        "message": "Order placed",
        "orders_placed": len(orders),
        "grand_total": order["total_amount"]
    }


@app.get("/orders")
def get_all_orders():
    return {
        "orders": orders,
        "total_orders": len(orders)
    }


from fastapi import FastAPI, HTTPException

app = FastAPI()

# ---------------------------------------
# Products Database
# ---------------------------------------
products = [
    {"id": 1, "name": "Wireless Mouse", "price": 499, "category": "Electronics", "in_stock": True},
    {"id": 2, "name": "Notebook", "price": 99, "category": "Stationery", "in_stock": True},
    {"id": 3, "name": "USB Hub", "price": 799, "category": "Electronics", "in_stock": False},
    {"id": 4, "name": "Pen Set", "price": 49, "category": "Stationery", "in_stock": True}
]

# ---------------------------------------
# Q1 – Search Products
# ---------------------------------------
@app.get("/products/search")
def search_products(keyword: str):

    results = []

    for product in products:
        if keyword.lower() in product["name"].lower():
            results.append(product)

    if not results:
        return {"message": f"No products found for: {keyword}"}

    return {
        "results": results,
        "total_found": len(results)
    }


# ---------------------------------------
# Q2 – Sort Products
# ---------------------------------------
@app.get("/products/sort")
def sort_products(sort_by: str = "price", order: str = "asc"):

    if sort_by not in ["price", "name"]:
        return {"error": "sort_by must be 'price' or 'name'"}

    reverse = True if order == "desc" else False

    sorted_products = sorted(products, key=lambda x: x[sort_by], reverse=reverse)

    return {
        "sort_by": sort_by,
        "order": order,
        "products": sorted_products
    }


# ---------------------------------------
# Q3 – Pagination
# ---------------------------------------
@app.get("/products/page")
def paginate_products(page: int = 1, limit: int = 2):

    total_products = len(products)
    total_pages = (total_products + limit - 1) // limit

    start = (page - 1) * limit
    end = start + limit

    paginated_products = products[start:end]

    return {
        "page": page,
        "limit": limit,
        "total_products": total_products,
        "total_pages": total_pages,
        "products": paginated_products
    }


# ---------------------------------------
# Q4 – Sort by Category then Price
# ---------------------------------------
@app.get("/products/sort-by-category")
def sort_by_category():

    sorted_products = sorted(products, key=lambda x: (x["category"], x["price"]))

    return {
        "products": sorted_products
    }


# ---------------------------------------
# Q5 – Orders Database
# ---------------------------------------
orders = []

@app.post("/orders")
def create_order(customer_name: str, product_id: int, quantity: int):

    for product in products:
        if product["id"] == product_id:

            order = {
                "order_id": len(orders) + 1,
                "customer_name": customer_name,
                "product_name": product["name"],
                "quantity": quantity,
                "total_price": product["price"] * quantity
            }

            orders.append(order)

            return {
                "message": "Order placed successfully",
                "order": order
            }

    raise HTTPException(status_code=404, detail="Product not found")


@app.get("/orders/search")
def search_orders(customer_name: str):

    results = []

    for order in orders:
        if customer_name.lower() in order["customer_name"].lower():
            results.append(order)

    if not results:
        return {"message": f"No orders found for: {customer_name}"}

    return {
        "customer_name": customer_name,
        "total_found": len(results),
        "orders": results
    }


# ---------------------------------------
# Q6 – Browse (Search + Sort + Pagination)
# ---------------------------------------
@app.get("/products/browse")
def browse_products(
    keyword: str = None,
    sort_by: str = "price",
    order: str = "asc",
    page: int = 1,
    limit: int = 4
):

    filtered_products = products

    # Filter by keyword
    if keyword:
        filtered_products = [
            p for p in filtered_products
            if keyword.lower() in p["name"].lower()
        ]

    # Sort
    if sort_by not in ["price", "name"]:
        return {"error": "sort_by must be 'price' or 'name'"}

    reverse = True if order == "desc" else False
    filtered_products = sorted(filtered_products, key=lambda x: x[sort_by], reverse=reverse)

    # Pagination
    total_found = len(filtered_products)
    total_pages = (total_found + limit - 1) // limit

    start = (page - 1) * limit
    end = start + limit

    paginated_products = filtered_products[start:end]

    return {
        "keyword": keyword,
        "sort_by": sort_by,
        "order": order,
        "page": page,
        "limit": limit,
        "total_found": total_found,
        "total_pages": total_pages,
        "products": paginated_products
    }


# ---------------------------------------
# Get Product by ID (MUST BE LAST)
# ---------------------------------------
@app.get("/products/{product_id}")
def get_product(product_id: int):

    for product in products:
        if product["id"] == product_id:
            return product

    raise HTTPException(status_code=404, detail="Product not found")


# ---------------------------------------
# BONUS – Paginate Orders
# ---------------------------------------
@app.get("/orders/page")
def paginate_orders(page: int = 1, limit: int = 3):

    total_orders = len(orders)
    total_pages = (total_orders + limit - 1) // limit

    start = (page - 1) * limit
    end = start + limit

    paginated_orders = orders[start:end]

    return {
        "page": page,
        "limit": limit,
        "total_orders": total_orders,
        "total_pages": total_pages,
        "orders": paginated_orders
    }
