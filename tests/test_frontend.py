#!/usr/bin/env python3
"""
UNITPLAST Frontend Tests - Landing Page & Mini App
Tests HTML structure, CSS, and frontend functionality
"""

import unittest
from bs4 import BeautifulSoup
from app.app import create_app

class TestLandingPage(unittest.TestCase):
    """Test landing page HTML structure"""

    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()
        response = self.client.get('/')
        self.html = response.get_data(as_text=True)
        self.soup = BeautifulSoup(self.html, 'html.parser')

    def test_landing_page_loads(self):
        """Test landing page HTTP status"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_landing_page_title(self):
        """Test landing page title"""
        title = self.soup.find('title')
        self.assertIsNotNone(title)
        self.assertIn('UNITPLAST', title.string)

    def test_landing_page_meta_description(self):
        """Test landing page meta description"""
        meta = self.soup.find('meta', attrs={'name': 'description'})
        self.assertIsNotNone(meta)

    def test_hero_section_exists(self):
        """Test hero section exists"""
        hero = self.soup.find('section', attrs={'class': 'hero'})
        self.assertIsNotNone(hero)

    def test_hero_title_exists(self):
        """Test hero title exists"""
        h1 = self.soup.find('h1')
        self.assertIsNotNone(h1)
        self.assertIn('30 секунд', h1.string)

    def test_features_section_exists(self):
        """Test features section exists"""
        features = self.soup.find('section', attrs={'class': 'features'})
        self.assertIsNotNone(features)

    def test_features_cards_count(self):
        """Test 6 feature cards exist"""
        feature_cards = self.soup.find_all('div', attrs={'class': 'feature-card'})
        self.assertEqual(len(feature_cards), 6)

    def test_three_brands_section(self):
        """Test three brands section exists"""
        brands = self.soup.find('section', attrs={'class': 'three-brands'})
        self.assertIsNotNone(brands)

    def test_brand_cards_count(self):
        """Test 3 brand cards exist"""
        brand_cards = self.soup.find_all('div', attrs={'class': 'brand-card'})
        self.assertEqual(len(brand_cards), 3)

    def test_brand_names_present(self):
        """Test UNITPLAST, UNIFURNITURE, UNIMETALL mentioned"""
        self.assertIn('UNITPLAST', self.html)
        self.assertIn('UNIFURNITURE', self.html)
        self.assertIn('UNIMETALL', self.html)

    def test_cta_buttons_exist(self):
        """Test CTA buttons exist"""
        buttons = self.soup.find_all('a', attrs={'class': 'btn-primary'})
        self.assertGreater(len(buttons), 0)

    def test_css_loaded(self):
        """Test CSS is linked"""
        link = self.soup.find('link', attrs={'rel': 'stylesheet'})
        self.assertIsNotNone(link)

    def test_fonts_linked(self):
        """Test Google Fonts are linked"""
        font_links = self.soup.find_all('link', attrs={'rel': 'preconnect'})
        self.assertGreater(len(font_links), 0)


class TestMiniApp(unittest.TestCase):
    """Test mini app structure"""

    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()
        response = self.client.get('/app/miniapp')
        self.html = response.get_data(as_text=True)
        self.soup = BeautifulSoup(self.html, 'html.parser')

    def test_miniapp_loads(self):
        """Test mini app HTTP status"""
        response = self.client.get('/app/miniapp')
        self.assertEqual(response.status_code, 200)

    def test_miniapp_title(self):
        """Test mini app title"""
        title = self.soup.find('title')
        self.assertIsNotNone(title)
        self.assertIn('UNITPLAST', title.string)

    def test_app_wrapper_exists(self):
        """Test app wrapper div exists"""
        wrapper = self.soup.find('div', attrs={'class': 'app-wrapper'})
        self.assertIsNotNone(wrapper)

    def test_dashboard_page_exists(self):
        """Test dashboard page element exists"""
        dashboard = self.soup.find('div', attrs={'id': 'page-dashboard'})
        self.assertIsNotNone(dashboard)

    def test_calculator_page_exists(self):
        """Test calculator page element exists"""
        calculator = self.soup.find('div', attrs={'id': 'page-calculator'})
        self.assertIsNotNone(calculator)

    def test_all_core_pages_exist(self):
        """Test all 27+ pages exist"""
        pages_to_check = [
            'page-dashboard',
            'page-calculator',
            'page-analytics',
            'page-profile',
            'page-team',
            'page-settings',
            'page-new-order',
            'page-notifications',
            'page-export-orders',
            'page-billing',
            'page-reports',
            'page-api-docs',
            'page-production-advanced',
            'page-materials-advanced'
        ]

        for page_id in pages_to_check:
            page = self.soup.find('div', attrs={'id': page_id})
            self.assertIsNotNone(page, f"Page {page_id} not found")

    def test_navigation_footer_exists(self):
        """Test footer navigation exists"""
        footer = self.soup.find('div', attrs={'class': 'app-footer'})
        self.assertIsNotNone(footer)

    def test_menu_modal_exists(self):
        """Test menu modal exists"""
        menu = self.soup.find('div', attrs={'id': 'menu-modal'})
        self.assertIsNotNone(menu)

    def test_header_exists(self):
        """Test app header exists"""
        header = self.soup.find('div', attrs={'class': 'app-header'})
        self.assertIsNotNone(header)

    def test_javascript_included(self):
        """Test JavaScript is included"""
        scripts = self.soup.find_all('script')
        self.assertGreater(len(scripts), 0)

    def test_page_count(self):
        """Test at least 27 pages exist"""
        pages = self.soup.find_all('div', attrs={'class': 'page'})
        self.assertGreaterEqual(len(pages), 27)


class TestResponsiveness(unittest.TestCase):
    """Test responsive design"""

    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()

    def test_viewport_meta_tag(self):
        """Test viewport meta tag exists"""
        response = self.client.get('/')
        html = response.get_data(as_text=True)
        self.assertIn('viewport', html)

    def test_landing_page_html_valid(self):
        """Test landing page HTML is well-formed"""
        response = self.client.get('/')
        html = response.get_data(as_text=True)
        soup = BeautifulSoup(html, 'html.parser')
        # Check for proper HTML structure
        self.assertIsNotNone(soup.find('html'))
        self.assertIsNotNone(soup.find('head'))
        self.assertIsNotNone(soup.find('body'))

    def test_miniapp_html_valid(self):
        """Test mini app HTML is well-formed"""
        response = self.client.get('/app/miniapp')
        html = response.get_data(as_text=True)
        soup = BeautifulSoup(html, 'html.parser')
        self.assertIsNotNone(soup.find('html'))
        self.assertIsNotNone(soup.find('head'))
        self.assertIsNotNone(soup.find('body'))


if __name__ == '__main__':
    unittest.main()
