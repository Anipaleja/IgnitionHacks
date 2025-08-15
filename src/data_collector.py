"""
Data collection module for gathering hardware information
"""

import asyncio
import json
import requests
from bs4 import BeautifulSoup
from pathlib import Path
from typing import Dict, List, Optional
import pandas as pd
from dataclasses import dataclass
import re
import time
from urllib.parse import urljoin, urlparse
import logging

from config import HARDWARE_COMPONENTS, DATA_SOURCES, RAW_DATA_DIR

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class HardwareData:
    """Data structure for hardware component information"""
    name: str
    category: str
    description: str
    pins: Dict[str, str]
    specifications: Dict[str, str]
    interfaces: List[str]
    voltage_range: str
    current_consumption: str
    operating_temperature: str
    code_examples: List[Dict[str, str]]
    connections: List[Dict[str, str]]
    datasheets: List[str]
    tutorials: List[str]

class DataCollector:
    """Collects hardware data from various sources"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
        self.hardware_data = {}
        
    def collect_wokwi_data(self, component_name: str) -> Dict:
        """Collect data from Wokwi documentation"""
        try:
            # Convert component name to URL format
            url_name = component_name.lower().replace(' ', '-').replace('(', '').replace(')', '')
            url = f"https://docs.wokwi.com/parts/wokwi-{url_name}"
            
            response = self.session.get(url)
            if response.status_code != 200:
                # Try alternative URL formats
                alternative_urls = [
                    f"https://docs.wokwi.com/parts/{url_name}",
                    f"https://docs.wokwi.com/guides/{url_name}",
                ]
                
                for alt_url in alternative_urls:
                    response = self.session.get(alt_url)
                    if response.status_code == 200:
                        break
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                data = {
                    'source': 'wokwi',
                    'url': response.url,
                    'title': soup.find('h1').get_text() if soup.find('h1') else component_name,
                    'description': self._extract_description(soup),
                    'pins': self._extract_pins_wokwi(soup),
                    'specifications': self._extract_specifications(soup),
                    'code_examples': self._extract_code_examples(soup),
                    'connections': self._extract_connections(soup)
                }
                
                logger.info(f"Successfully collected Wokwi data for {component_name}")
                return data
                
        except Exception as e:
            logger.error(f"Error collecting Wokwi data for {component_name}: {e}")
        
        return {}
    
    def collect_arduino_reference(self, component_name: str) -> Dict:
        """Collect data from Arduino reference"""
        try:
            search_url = f"https://www.arduino.cc/search?q={component_name}"
            response = self.session.get(search_url)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                # Extract relevant Arduino documentation
                data = {
                    'source': 'arduino',
                    'libraries': self._extract_arduino_libraries(soup, component_name),
                    'functions': self._extract_arduino_functions(soup),
                    'examples': self._extract_arduino_examples(soup)
                }
                
                logger.info(f"Successfully collected Arduino data for {component_name}")
                return data
                
        except Exception as e:
            logger.error(f"Error collecting Arduino data for {component_name}: {e}")
        
        return {}
    
    def collect_component_datasheet_info(self, component_name: str) -> Dict:
        """Collect datasheet information from various sources"""
        try:
            # Search for component on popular electronics sites
            search_terms = [
                f"{component_name} datasheet",
                f"{component_name} pinout",
                f"{component_name} specifications"
            ]
            
            collected_data = []
            
            for term in search_terms:
                # Search Components101
                data = self._search_components101(term)
                if data:
                    collected_data.append(data)
                
                # Search SparkFun
                data = self._search_sparkfun(term)
                if data:
                    collected_data.append(data)
                
                time.sleep(1)  # Rate limiting
            
            return {
                'source': 'datasheets',
                'data': collected_data
            }
            
        except Exception as e:
            logger.error(f"Error collecting datasheet info for {component_name}: {e}")
        
        return {}
    
    def _extract_description(self, soup: BeautifulSoup) -> str:
        """Extract component description from HTML"""
        # Look for description in various common patterns
        patterns = [
            ('p', {'class': 'description'}),
            ('div', {'class': 'description'}),
            ('p', {}),  # First paragraph after h1
        ]
        
        for tag, attrs in patterns:
            elements = soup.find_all(tag, attrs)
            for elem in elements:
                text = elem.get_text().strip()
                if len(text) > 50:  # Reasonable description length
                    return text
        
        return ""
    
    def _extract_pins_wokwi(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Extract pin information from Wokwi documentation"""
        pins = {}
        
        # Look for pin tables or lists
        tables = soup.find_all('table')
        for table in tables:
            headers = [th.get_text().strip().lower() for th in table.find_all('th')]
            if 'pin' in ' '.join(headers):
                rows = table.find_all('tr')[1:]  # Skip header
                for row in rows:
                    cells = [td.get_text().strip() for td in row.find_all('td')]
                    if len(cells) >= 2:
                        pin_name = cells[0]
                        pin_desc = cells[1]
                        pins[pin_name] = pin_desc
        
        # Also look for pin lists
        pin_lists = soup.find_all(['ul', 'ol'])
        for pin_list in pin_lists:
            items = pin_list.find_all('li')
            for item in items:
                text = item.get_text().strip()
                if ':' in text:
                    parts = text.split(':', 1)
                    if len(parts) == 2:
                        pin_name = parts[0].strip()
                        pin_desc = parts[1].strip()
                        pins[pin_name] = pin_desc
        
        return pins
    
    def _extract_specifications(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Extract technical specifications"""
        specs = {}
        
        # Look for specification tables
        tables = soup.find_all('table')
        for table in tables:
            rows = table.find_all('tr')
            for row in rows:
                cells = row.find_all(['td', 'th'])
                if len(cells) == 2:
                    key = cells[0].get_text().strip()
                    value = cells[1].get_text().strip()
                    if key and value:
                        specs[key] = value
        
        return specs
    
    def _extract_code_examples(self, soup: BeautifulSoup) -> List[Dict[str, str]]:
        """Extract code examples from documentation"""
        examples = []
        
        # Look for code blocks
        code_blocks = soup.find_all(['pre', 'code'])
        for i, block in enumerate(code_blocks):
            code = block.get_text().strip()
            if len(code) > 50:  # Reasonable code length
                examples.append({
                    'title': f"Example {i+1}",
                    'code': code,
                    'language': self._detect_language(code)
                })
        
        return examples
    
    def _extract_connections(self, soup: BeautifulSoup) -> List[Dict[str, str]]:
        """Extract connection information"""
        connections = []
        
        # Look for connection descriptions
        text = soup.get_text().lower()
        connection_patterns = [
            r'connect\s+(\w+)\s+to\s+(\w+)',
            r'wire\s+(\w+)\s+to\s+(\w+)',
            r'(\w+)\s+pin\s+to\s+(\w+)'
        ]
        
        for pattern in connection_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                connections.append({
                    'from': match[0],
                    'to': match[1]
                })
        
        return connections
    
    def _detect_language(self, code: str) -> str:
        """Detect programming language of code snippet"""
        if '#include' in code or 'void setup()' in code:
            return 'arduino'
        elif 'import' in code and 'def ' in code:
            return 'python'
        elif 'function' in code or 'const ' in code:
            return 'javascript'
        else:
            return 'unknown'
    
    def _search_components101(self, search_term: str) -> Optional[Dict]:
        """Search Components101 for component information"""
        try:
            url = f"https://components101.com/search?q={search_term}"
            response = self.session.get(url)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                # Extract relevant information
                return {
                    'site': 'components101',
                    'url': url,
                    'content': soup.get_text()[:1000]  # First 1000 chars
                }
        except Exception as e:
            logger.error(f"Error searching Components101: {e}")
        
        return None
    
    def _search_sparkfun(self, search_term: str) -> Optional[Dict]:
        """Search SparkFun for component information"""
        try:
            url = f"https://www.sparkfun.com/search/results?term={search_term}"
            response = self.session.get(url)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                return {
                    'site': 'sparkfun',
                    'url': url,
                    'content': soup.get_text()[:1000]
                }
        except Exception as e:
            logger.error(f"Error searching SparkFun: {e}")
        
        return None
    
    def _extract_arduino_libraries(self, soup: BeautifulSoup, component_name: str) -> List[str]:
        """Extract Arduino libraries related to component"""
        libraries = []
        text = soup.get_text().lower()
        
        # Common library patterns
        lib_patterns = [
            rf'{component_name.lower()}\.h',
            rf'lib{component_name.lower()}',
            rf'{component_name.lower()}library'
        ]
        
        for pattern in lib_patterns:
            matches = re.findall(pattern, text)
            libraries.extend(matches)
        
        return list(set(libraries))
    
    def _extract_arduino_functions(self, soup: BeautifulSoup) -> List[str]:
        """Extract Arduino functions from documentation"""
        functions = []
        
        # Look for function definitions
        code_blocks = soup.find_all(['pre', 'code'])
        for block in code_blocks:
            code = block.get_text()
            # Arduino function pattern
            func_matches = re.findall(r'(\w+)\s*\([^)]*\)\s*{', code)
            functions.extend(func_matches)
        
        return list(set(functions))
    
    def _extract_arduino_examples(self, soup: BeautifulSoup) -> List[Dict]:
        """Extract Arduino example codes"""
        examples = []
        
        # Look for example sections
        sections = soup.find_all(['div', 'section'])
        for section in sections:
            if 'example' in section.get_text().lower()[:100]:
                code_blocks = section.find_all(['pre', 'code'])
                for block in code_blocks:
                    code = block.get_text().strip()
                    if 'void setup()' in code or 'void loop()' in code:
                        examples.append({
                            'code': code,
                            'type': 'arduino_sketch'
                        })
        
        return examples
    
    async def collect_all_data(self) -> Dict:
        """Collect data for all hardware components"""
        all_data = {}
        
        for component in HARDWARE_COMPONENTS:
            component_name = component['name']
            logger.info(f"Collecting data for {component_name}")
            
            component_data = {
                'config': component,
                'wokwi': self.collect_wokwi_data(component_name),
                'arduino': self.collect_arduino_reference(component_name),
                'datasheets': self.collect_component_datasheet_info(component_name)
            }
            
            all_data[component_name] = component_data
            
            # Rate limiting
            await asyncio.sleep(2)
        
        return all_data
    
    def save_collected_data(self, data: Dict, filename: str = "hardware_data.json"):
        """Save collected data to file"""
        filepath = RAW_DATA_DIR / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Data saved to {filepath}")
    
    def load_collected_data(self, filename: str = "hardware_data.json") -> Dict:
        """Load previously collected data"""
        filepath = RAW_DATA_DIR / filename
        
        if filepath.exists():
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        return {}

async def main():
    """Main data collection function"""
    collector = DataCollector()
    
    # Check if data already exists
    existing_data = collector.load_collected_data()
    
    if not existing_data:
        logger.info("Starting data collection...")
        collected_data = await collector.collect_all_data()
        collector.save_collected_data(collected_data)
        logger.info("Data collection completed!")
    else:
        logger.info("Using existing collected data")
        collected_data = existing_data
    
    return collected_data

if __name__ == "__main__":
    asyncio.run(main())
