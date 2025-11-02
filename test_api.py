#!/usr/bin/env python3

import requests
import json
from typing import Dict, Optional

BASE_URL = "http://localhost:5000/api"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    YELLOW = '\033[93m'
    RESET = '\033[0m'

def print_test(name: str):
    print(f"\n{Colors.BLUE}{'='*60}{Colors.RESET}")
    print(f"{Colors.BLUE}TEST: {name}{Colors.RESET}")
    print(f"{Colors.BLUE}{'='*60}{Colors.RESET}")

def print_success(message: str):
    print(f"{Colors.GREEN}✓ {message}{Colors.RESET}")

def print_error(message: str):
    print(f"{Colors.RED}✗ {message}{Colors.RESET}")

def print_info(message: str):
    print(f"{Colors.YELLOW}ℹ {message}{Colors.RESET}")

def make_request(method: str, endpoint: str, token: Optional[str] = None, data: Optional[Dict] = None):
    url = f"{BASE_URL}{endpoint}"
    headers = {"Content-Type": "application/json"}
    
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=data)
        elif method == "PATCH":
            response = requests.patch(url, headers=headers, json=data)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers)
        else:
            raise ValueError(f"Unsupported method: {method}")
        
        return response
    except requests.exceptions.ConnectionError:
        print_error("Cannot connect to API. Is the server running?")
        return None

def test_health_check():
    print_test("Health Check")
    response = make_request("GET", "/health")
    
    if response and response.status_code == 200:
        print_success("Health check passed")
        print_info(f"Response: {response.json()}")
        return True
    else:
        print_error("Health check failed")
        return False

def test_login(email: str, password: str, expected_role: str):
    print_test(f"Login as {expected_role}")
    
    response = make_request("POST", "/login", data={
        "email": email,
        "password": password
    })
    
    if response and response.status_code == 200:
        data = response.json()
        token = data.get('token')
        user = data.get('user')
        
        if user.get('role') == expected_role:
            print_success(f"Login successful as {user['first_name']} {user['last_name']} ({expected_role})")
            print_info(f"User ID: {user['id']}")
            print_info(f"Role ID: {user['role_id']}")
            return token
        else:
            print_error(f"Expected role '{expected_role}' but got '{user.get('role')}'")
            return None
    else:
        print_error(f"Login failed: {response.text if response else 'No response'}")
        return None

def test_dashboard(token: str, role: str):
    print_test(f"Dashboard - {role}")
    
    response = make_request("GET", "/dashboard", token=token)
    
    if response and response.status_code == 200:
        data = response.json()
        print_success("Dashboard loaded successfully")
        print_info(f"Role in dashboard: {data.get('role', 'N/A')}")
        
        if 'statistics' in data:
            print_info("Statistics:")
            for key, value in data['statistics'].items():
                print(f"  - {key}: {value}")
        
        return True
    else:
        print_error(f"Dashboard failed: {response.text if response else 'No response'}")
        return False

def test_get_orders(token: str, role: str):
    print_test(f"Get Orders - {role}")
    
    response = make_request("GET", "/orders", token=token)
    
    if response and response.status_code == 200:
        data = response.json()
        orders = data.get('orders', [])
        print_success(f"Retrieved {len(orders)} orders")
        
        if orders:
            print_info("First order:")
            print(f"  - Order Number: {orders[0].get('order_number')}")
            print(f"  - Status: {orders[0].get('status')}")
        
        return True
    else:
        print_error(f"Get orders failed: {response.text if response else 'No response'}")
        return False

def test_create_order(token: str):
    print_test("Create Order (Manager)")
    
    response = make_request("POST", "/orders", token=token, data={
        "order_number": "PO-TEST-001",
        "vendor_id": 1
    })
    
    if response and response.status_code == 201:
        data = response.json()
        print_success(f"Order created: {data['order']['order_number']}")
        return data['order']['id']
    elif response and response.status_code == 400:
        print_info("Order number already exists (expected if re-running tests)")
        return None
    else:
        print_error(f"Create order failed: {response.text if response else 'No response'}")
        return None

def test_get_quotes(token: str, role: str):
    print_test(f"Get Quotes - {role}")
    
    response = make_request("GET", "/quotes", token=token)
    
    if response and response.status_code == 200:
        data = response.json()
        quotes = data.get('quotes', [])
        print_success(f"Retrieved {len(quotes)} quotes")
        
        if quotes:
            print_info("First quote:")
            print(f"  - Price: ${quotes[0].get('price')}")
            print(f"  - Status: {quotes[0].get('status')}")
        
        return True
    else:
        print_error(f"Get quotes failed: {response.text if response else 'No response'}")
        return False

def test_submit_quote(token: str, order_id: int):
    print_test("Submit Quote (Vendor)")
    
    response = make_request("POST", "/quotes", token=token, data={
        "order_id": order_id,
        "price": 25000.00,
        "notes": "Test quote - competitive pricing"
    })
    
    if response and response.status_code == 201:
        data = response.json()
        print_success(f"Quote submitted: ${data['quote']['price']}")
        return data['quote']['id']
    elif response and response.status_code == 400:
        print_info("Quote already exists for this order (expected if re-running tests)")
        return None
    else:
        print_error(f"Submit quote failed: {response.text if response else 'No response'}")
        return None

def test_get_vendors(token: str):
    print_test("Get Vendors")
    
    response = make_request("GET", "/vendors", token=token)
    
    if response and response.status_code == 200:
        data = response.json()
        vendors = data.get('vendors', [])
        print_success(f"Retrieved {len(vendors)} vendors")
        
        for vendor in vendors[:3]:
            verified = "✓" if vendor.get('is_verified') else "✗"
            print_info(f"  {verified} {vendor.get('name')} - {vendor.get('email')}")
        
        return True
    else:
        print_error(f"Get vendors failed: {response.text if response else 'No response'}")
        return False

def test_get_requirements(token: str):
    print_test("Get Requirements (Manager)")
    
    response = make_request("GET", "/requirements", token=token)
    
    if response and response.status_code == 200:
        data = response.json()
        requirements = data.get('requirements', [])
        print_success(f"Retrieved {len(requirements)} requirements")
        
        if requirements:
            for req in requirements[:3]:
                print_info(f"  - {req.get('item_name')}: {req.get('quantity')} units")
        
        return True
    else:
        print_error(f"Get requirements failed: {response.text if response else 'No response'}")
        return False

def test_register_vendor():
    print_test("Register New Vendor")
    
    response = make_request("POST", "/register", data={
        "email": "newvendor@test.com",
        "password": "password123",
        "first_name": "Test",
        "last_name": "Vendor",
        "phone": "0700000999",
        "company_name": "Test Vendor Co"
    })
    
    if response and response.status_code == 201:
        data = response.json()
        print_success(f"Vendor registered: {data['user']['email']}")
        print_info("Note: New vendors need manager approval (is_verified=False)")
        return data.get('token')
    elif response and response.status_code == 400:
        print_info("Email already exists (expected if re-running tests)")
        return None
    else:
        print_error(f"Registration failed: {response.text if response else 'No response'}")
        return None

def run_all_tests():
    print(f"\n{Colors.BLUE}{'='*60}")
    print("🧪 VENDORSYNC API TEST SUITE")
    print(f"{'='*60}{Colors.RESET}\n")
    
    if not test_health_check():
        print_error("\n❌ Server is not running. Please start the backend server.")
        return
    
    print_info("\n" + "="*60)
    print_info("Testing Manager Flow")
    print_info("="*60)
    
    manager_token = test_login("manager@example.com", "password123", "manager")
    if manager_token:
        test_dashboard(manager_token, "manager")
        test_get_orders(manager_token, "manager")
        test_get_vendors(manager_token)
        test_get_requirements(manager_token)
        order_id = test_create_order(manager_token)
    
    print_info("\n" + "="*60)
    print_info("Testing Staff Flow")
    print_info("="*60)
    
    staff_token = test_login("staff@example.com", "password123", "staff")
    if staff_token:
        test_dashboard(staff_token, "staff")
        test_get_orders(staff_token, "staff")
    
    print_info("\n" + "="*60)
    print_info("Testing Vendor Flow")
    print_info("="*60)
    
    vendor_token = test_login("vendor@example.com", "password123", "vendor")
    if vendor_token:
        test_dashboard(vendor_token, "vendor")
        test_get_orders(vendor_token, "vendor")
        test_get_quotes(vendor_token, "vendor")
        
        if 'order_id' in locals():
            test_submit_quote(vendor_token, order_id)
    
    print_info("\n" + "="*60)
    print_info("Testing Vendor Registration")
    print_info("="*60)
    test_register_vendor()
    
    print(f"\n{Colors.BLUE}{'='*60}")
    print("✅ TEST SUITE COMPLETED")
    print(f"{'='*60}{Colors.RESET}\n")

if __name__ == "__main__":
    run_all_tests()