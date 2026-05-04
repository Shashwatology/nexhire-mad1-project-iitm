import os
from playwright.sync_api import sync_playwright

def take_screenshots():
    # Ensure static/assets exists
    os.makedirs('static/assets', exist_ok=True)
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1280, 'height': 800})
        page = context.new_page()
        
        # 1. Landing Page
        print("Taking screenshot of landing page...")
        page.goto('http://127.0.0.1:5000/')
        page.wait_for_timeout(2000) # Wait for animations
        page.screenshot(path='static/assets/landing.png', full_page=True)
        
        # 2. Login Page
        print("Taking screenshot of login page...")
        page.goto('http://127.0.0.1:5000/login')
        page.wait_for_timeout(1000)
        page.screenshot(path='static/assets/login.png', full_page=True)
        
        # 3. Login as Admin
        print("Logging in as admin...")
        page.fill('input[name="username"]', 'admin')
        page.fill('input[name="password"]', 'admin')
        page.click('button[type="submit"]')
        
        # Wait for dashboard to load
        page.wait_for_url('**/admin/dashboard')
        page.wait_for_timeout(1500)
        
        print("Taking screenshot of admin dashboard...")
        page.screenshot(path='static/assets/admin_dashboard.png', full_page=True)
        
        browser.close()
        print("Screenshots taken successfully.")

if __name__ == '__main__':
    take_screenshots()
