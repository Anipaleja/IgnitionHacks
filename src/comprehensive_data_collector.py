"""
Comprehensive Hardware Knowledge Extractor
Collects EVERYTHING about hardware components - physical characteristics, 
pin colors, detailed specifications, wiring diagrams, troubleshooting, etc.
"""

import asyncio
import json
import requests
from bs4 import BeautifulSoup, Comment
from pathlib import Path
from typing import Dict, List, Optional, Any
import pandas as pd
from dataclasses import dataclass, asdict
import re
import time
from urllib.parse import urljoin, urlparse
import logging
import aiohttp
import concurrent.futures
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import base64
import io
from PIL import Image

from config import HARDWARE_COMPONENTS, RAW_DATA_DIR

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ComprehensiveHardwareData:
    """Complete hardware component data structure"""
    name: str
    category: str
    
    # Physical Characteristics
    physical_description: str
    dimensions: Dict[str, str]  # length, width, height, weight
    color_scheme: Dict[str, str]  # body_color, pin_colors, markings
    package_type: str  # DIP, SMD, module, breakout, etc.
    mounting_style: str  # through-hole, surface-mount, etc.
    
    # Pin Information (DETAILED)
    pin_count: int
    pin_layout: str  # description of physical layout
    pin_colors: Dict[str, str]  # pin number/name to color mapping
    pin_functions: Dict[str, Dict[str, Any]]  # pin -> {function, voltage, current, etc}
    pin_dimensions: Dict[str, str]  # pin spacing, diameter, etc.
    
    # Electrical Specifications (COMPREHENSIVE)
    voltage_specs: Dict[str, str]  # operating, absolute max, etc.
    current_specs: Dict[str, str]  # operating, max, startup, etc.
    power_consumption: Dict[str, str]  # active, sleep, max, etc.
    frequency_specs: Dict[str, str]  # clock, communication, etc.
    impedance_specs: Dict[str, str]  # input, output impedance
    
    # Interface Details
    communication_interfaces: List[Dict[str, Any]]  # protocol, pins, config
    analog_interfaces: List[Dict[str, Any]]  # ADC, DAC details
    digital_interfaces: List[Dict[str, Any]]  # GPIO, PWM details
    
    # Wiring and Connections (DETAILED)
    typical_connections: List[Dict[str, Any]]  # common wiring scenarios
    wiring_diagrams: List[str]  # URLs or descriptions
    connection_examples: List[Dict[str, Any]]  # step-by-step wiring
    common_mistakes: List[str]  # wiring mistakes to avoid
    
    # Programming and Code
    required_libraries: List[Dict[str, Any]]  # library, version, purpose
    initialization_code: List[Dict[str, str]]  # language, code
    example_functions: List[Dict[str, Any]]  # function, parameters, usage
    advanced_features: List[Dict[str, Any]]  # advanced usage examples
    
    # Environmental and Operating Conditions
    temperature_range: Dict[str, str]  # operating, storage
    humidity_range: str
    environmental_protection: str  # IP rating, etc.
    certifications: List[str]  # CE, FCC, etc.
    
    # Troubleshooting and Debugging
    common_issues: List[Dict[str, str]]  # problem, solution
    debugging_tips: List[str]
    testing_procedures: List[Dict[str, Any]]  # test, expected result
    
    # Compatibility and Integration
    compatible_boards: List[str]  # microcontrollers it works with
    voltage_level_compatibility: Dict[str, List[str]]  # 3.3V, 5V boards
    shield_compatibility: List[str]  # Arduino shields, etc.
    
    # Performance Characteristics
    accuracy_precision: Dict[str, str]  # for sensors
    response_time: Dict[str, str]  # delays, timing
    bandwidth_throughput: Dict[str, str]  # data rates
    
    # Mechanical Information
    connector_types: List[Dict[str, Any]]  # connector details
    mechanical_drawings: List[str]  # technical drawings
    assembly_instructions: List[str]  # how to mount/connect
    
    # Manufacturer Information
    manufacturer: str
    part_number: str
    datasheet_url: str
    alternative_parts: List[str]  # equivalent components
    
    # Additional Resources
    tutorials: List[Dict[str, str]]  # title, url, difficulty
    community_projects: List[Dict[str, str]]  # project examples
    documentation_links: List[str]
    video_resources: List[str]

class ComprehensiveDataCollector:
    """Collects comprehensive hardware data from multiple sources"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        
        # Setup Selenium for dynamic content
        self.setup_selenium()
        
        # Comprehensive data sources
        self.data_sources = {
            'datasheets': [
                'https://www.alldatasheet.com/datasheet-pdf/pdf/',
                'https://datasheetspdf.com/',
                'https://www.datasheets360.com/',
            ],
            'tutorials': [
                'https://randomnerdtutorials.com/',
                'https://learn.adafruit.com/',
                'https://www.sparkfun.com/tutorials',
                'https://www.electronicshub.org/',
                'https://create.arduino.cc/projecthub',
                'https://www.instructables.com/',
            ],
            'documentation': [
                'https://docs.wokwi.com/',
                'https://www.arduino.cc/reference/',
                'https://docs.espressif.com/',
                'https://www.raspberrypi.org/documentation/',
            ],
            'forums': [
                'https://forum.arduino.cc/',
                'https://www.reddit.com/r/arduino/',
                'https://www.reddit.com/r/esp32/',
                'https://stackoverflow.com/',
            ],
            'component_databases': [
                'https://components101.com/',
                'https://www.electronicshub.org/',
                'https://lastminuteengineers.com/',
                'https://circuitdigest.com/',
            ]
        }
    
    def setup_selenium(self):
        """Setup Selenium WebDriver for dynamic content"""
        try:
            chrome_options = Options()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
            
            self.driver = webdriver.Chrome(options=chrome_options)
            logger.info("Selenium WebDriver initialized")
        except Exception as e:
            logger.warning(f"Selenium setup failed: {e}. Will use requests only.")
            self.driver = None
    
    async def collect_comprehensive_data(self, component: Dict) -> ComprehensiveHardwareData:
        """Collect comprehensive data for a single component"""
        
        component_name = component['name']
        logger.info(f"Collecting comprehensive data for {component_name}")
        
        # Initialize data structure
        comp_data = ComprehensiveHardwareData(
            name=component_name,
            category=component['category'],
            physical_description="",
            dimensions={},
            color_scheme={},
            package_type="",
            mounting_style="",
            pin_count=component.get('pins', 0),
            pin_layout="",
            pin_colors={},
            pin_functions={},
            pin_dimensions={},
            voltage_specs={},
            current_specs={},
            power_consumption={},
            frequency_specs={},
            impedance_specs={},
            communication_interfaces=[],
            analog_interfaces=[],
            digital_interfaces=[],
            typical_connections=[],
            wiring_diagrams=[],
            connection_examples=[],
            common_mistakes=[],
            required_libraries=[],
            initialization_code=[],
            example_functions=[],
            advanced_features=[],
            temperature_range={},
            humidity_range="",
            environmental_protection="",
            certifications=[],
            common_issues=[],
            debugging_tips=[],
            testing_procedures=[],
            compatible_boards=[],
            voltage_level_compatibility={},
            shield_compatibility=[],
            accuracy_precision={},
            response_time={},
            bandwidth_throughput={},
            connector_types=[],
            mechanical_drawings=[],
            assembly_instructions=[],
            manufacturer="",
            part_number="",
            datasheet_url="",
            alternative_parts=[],
            tutorials=[],
            community_projects=[],
            documentation_links=[],
            video_resources=[]
        )
        
        # Collect from multiple sources in parallel
        tasks = [
            self.collect_datasheet_info(component_name, comp_data),
            self.collect_tutorial_info(component_name, comp_data),
            self.collect_wokwi_detailed_info(component_name, comp_data),
            self.collect_arduino_detailed_info(component_name, comp_data),
            self.collect_component_database_info(component_name, comp_data),
            self.collect_forum_discussions(component_name, comp_data),
            self.collect_manufacturer_info(component_name, comp_data),
            self.collect_pinout_diagrams(component_name, comp_data),
            self.collect_wiring_examples(component_name, comp_data),
            self.collect_troubleshooting_info(component_name, comp_data)
        ]
        
        # Execute all collection tasks
        await asyncio.gather(*tasks, return_exceptions=True)
        
        logger.info(f"Comprehensive data collection completed for {component_name}")
        return comp_data
    
    async def collect_datasheet_info(self, component_name: str, comp_data: ComprehensiveHardwareData):
        """Collect detailed datasheet information"""
        logger.info(f"📄 Collecting datasheet info for {component_name}")
        
        try:
            # Search for official datasheets
            search_terms = [
                f"{component_name} datasheet",
                f"{component_name} pinout diagram",
                f"{component_name} electrical characteristics",
                f"{component_name} specifications"
            ]
            
            for term in search_terms:
                # Search multiple datasheet sources
                for source in self.data_sources['datasheets']:
                    data = await self._search_datasheet_source(source, term)
                    if data:
                        self._extract_datasheet_data(data, comp_data)
                
                await asyncio.sleep(0.5)  # Rate limiting
                
        except Exception as e:
            logger.error(f"Datasheet collection error for {component_name}: {e}")
    
    async def collect_pinout_diagrams(self, component_name: str, comp_data: ComprehensiveHardwareData):
        """Collect detailed pinout information including colors and physical layout"""
        logger.info(f"📍 Collecting pinout diagrams for {component_name}")
        
        try:
            # Search for pinout-specific information
            pinout_searches = [
                f"{component_name} pinout diagram color",
                f"{component_name} pin layout physical",
                f"{component_name} pin assignment detailed",
                f"{component_name} connector pinout"
            ]
            
            for search in pinout_searches:
                # Use multiple sources for pinout information
                pinout_data = await self._search_pinout_info(search)
                if pinout_data:
                    self._extract_pinout_details(pinout_data, comp_data)
                
                await asyncio.sleep(0.3)
                
        except Exception as e:
            logger.error(f"Pinout collection error for {component_name}: {e}")
    
    async def collect_wiring_examples(self, component_name: str, comp_data: ComprehensiveHardwareData):
        """Collect comprehensive wiring examples and connection details"""
        logger.info(f"Collecting wiring examples for {component_name}")
        
        try:
            # Search for wiring-specific tutorials
            wiring_searches = [
                f"{component_name} wiring diagram tutorial",
                f"how to connect {component_name} step by step",
                f"{component_name} breadboard wiring",
                f"{component_name} PCB connection",
                f"{component_name} common wiring mistakes"
            ]
            
            for search in wiring_searches:
                wiring_data = await self._search_wiring_tutorials(search)
                if wiring_data:
                    self._extract_wiring_details(wiring_data, comp_data)
                
                await asyncio.sleep(0.3)
                
        except Exception as e:
            logger.error(f"Wiring collection error for {component_name}: {e}")
    
    async def collect_troubleshooting_info(self, component_name: str, comp_data: ComprehensiveHardwareData):
        """Collect troubleshooting and debugging information"""
        logger.info(f"Collecting troubleshooting info for {component_name}")
        
        try:
            # Search for troubleshooting guides
            troubleshooting_searches = [
                f"{component_name} troubleshooting guide",
                f"{component_name} common problems solutions",
                f"{component_name} not working debug",
                f"{component_name} testing procedure",
                f"{component_name} debugging tips"
            ]
            
            for search in troubleshooting_searches:
                debug_data = await self._search_troubleshooting_info(search)
                if debug_data:
                    self._extract_troubleshooting_details(debug_data, comp_data)
                
                await asyncio.sleep(0.3)
                
        except Exception as e:
            logger.error(f"Troubleshooting collection error for {component_name}: {e}")
    
    async def collect_tutorial_info(self, component_name: str, comp_data: ComprehensiveHardwareData):
        """Collect tutorial and project information"""
        logger.info(f"Collecting tutorial info for {component_name}")
        
        try:
            # Search tutorial sites
            for tutorial_site in self.data_sources['tutorials']:
                tutorial_data = await self._search_tutorial_site(tutorial_site, component_name)
                if tutorial_data:
                    self._extract_tutorial_data(tutorial_data, comp_data)
                
                await asyncio.sleep(0.5)
                
        except Exception as e:
            logger.error(f"Tutorial collection error for {component_name}: {e}")
    
    async def collect_wokwi_detailed_info(self, component_name: str, comp_data: ComprehensiveHardwareData):
        """Collect detailed Wokwi information"""
        logger.info(f"Collecting Wokwi detailed info for {component_name}")
        
        try:
            url_variants = [
                f"https://docs.wokwi.com/parts/wokwi-{component_name.lower().replace(' ', '-').replace('(', '').replace(')', '')}",
                f"https://docs.wokwi.com/parts/{component_name.lower().replace(' ', '-')}",
                f"https://docs.wokwi.com/guides/{component_name.lower().replace(' ', '-')}"
            ]
            
            for url in url_variants:
                try:
                    response = self.session.get(url, timeout=10)
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        self._extract_wokwi_detailed_data(soup, comp_data)
                        break
                except:
                    continue
                    
        except Exception as e:
            logger.error(f"Wokwi detailed collection error for {component_name}: {e}")
    
    async def collect_arduino_detailed_info(self, component_name: str, comp_data: ComprehensiveHardwareData):
        """Collect detailed Arduino information"""
        logger.info(f"Collecting Arduino detailed info for {component_name}")
        
        try:
            # Search Arduino ecosystem
            arduino_searches = [
                f"site:arduino.cc {component_name}",
                f"site:create.arduino.cc {component_name}",
                f"{component_name} Arduino library",
                f"{component_name} Arduino example code"
            ]
            
            for search in arduino_searches:
                arduino_data = await self._search_arduino_ecosystem(search)
                if arduino_data:
                    self._extract_arduino_detailed_data(arduino_data, comp_data)
                
                await asyncio.sleep(0.3)
                
        except Exception as e:
            logger.error(f"Arduino detailed collection error for {component_name}: {e}")
    
    async def collect_component_database_info(self, component_name: str, comp_data: ComprehensiveHardwareData):
        """Collect information from component databases"""
        logger.info(f"🗃️ Collecting component database info for {component_name}")
        
        try:
            for db_site in self.data_sources['component_databases']:
                db_data = await self._search_component_database(db_site, component_name)
                if db_data:
                    self._extract_component_database_data(db_data, comp_data)
                
                await asyncio.sleep(0.5)
                
        except Exception as e:
            logger.error(f"Component database collection error for {component_name}: {e}")
    
    async def collect_forum_discussions(self, component_name: str, comp_data: ComprehensiveHardwareData):
        """Collect forum discussions and community knowledge"""
        logger.info(f"💬 Collecting forum discussions for {component_name}")
        
        try:
            # Search forums for real-world usage patterns
            forum_searches = [
                f"{component_name} problems forum",
                f"{component_name} tips tricks",
                f"{component_name} project examples",
                f"{component_name} best practices"
            ]
            
            for search in forum_searches:
                forum_data = await self._search_forums(search)
                if forum_data:
                    self._extract_forum_knowledge(forum_data, comp_data)
                
                await asyncio.sleep(0.3)
                
        except Exception as e:
            logger.error(f"Forum collection error for {component_name}: {e}")
    
    async def collect_manufacturer_info(self, component_name: str, comp_data: ComprehensiveHardwareData):
        """Collect manufacturer information and specifications"""
        logger.info(f"🏭 Collecting manufacturer info for {component_name}")
        
        try:
            # Search for manufacturer pages
            manufacturer_searches = [
                f"{component_name} manufacturer specification",
                f"{component_name} official datasheet",
                f"{component_name} part number",
                f"{component_name} technical specifications"
            ]
            
            for search in manufacturer_searches:
                mfg_data = await self._search_manufacturer_info(search)
                if mfg_data:
                    self._extract_manufacturer_data(mfg_data, comp_data)
                
                await asyncio.sleep(0.3)
                
        except Exception as e:
            logger.error(f"Manufacturer collection error for {component_name}: {e}")
    
    # Helper methods for data extraction
    def _extract_datasheet_data(self, data: Dict, comp_data: ComprehensiveHardwareData):
        """Extract detailed information from datasheet data"""
        # Implementation for extracting voltage specs, current specs, etc.
        pass
    
    def _extract_pinout_details(self, data: Dict, comp_data: ComprehensiveHardwareData):
        """Extract detailed pinout information including colors"""
        # Implementation for extracting pin colors, layout, functions
        pass
    
    def _extract_wiring_details(self, data: Dict, comp_data: ComprehensiveHardwareData):
        """Extract wiring diagrams and connection examples"""
        # Implementation for extracting wiring information
        pass
    
    def _extract_troubleshooting_details(self, data: Dict, comp_data: ComprehensiveHardwareData):
        """Extract troubleshooting and debugging information"""
        # Implementation for extracting troubleshooting data
        pass
    
    # Search helper methods
    async def _search_datasheet_source(self, source: str, term: str) -> Optional[Dict]:
        """Search datasheet sources"""
        # Implementation for searching datasheet sources
        return None
    
    async def _search_pinout_info(self, search: str) -> Optional[Dict]:
        """Search for pinout information"""
        # Implementation for pinout search
        return None
    
    async def _search_wiring_tutorials(self, search: str) -> Optional[Dict]:
        """Search for wiring tutorials"""
        # Implementation for wiring tutorial search
        return None
    
    async def _search_troubleshooting_info(self, search: str) -> Optional[Dict]:
        """Search for troubleshooting information"""
        # Implementation for troubleshooting search
        return None
    
    # Additional helper methods...
    async def _search_tutorial_site(self, site: str, component: str) -> Optional[Dict]:
        return None
    
    async def _search_arduino_ecosystem(self, search: str) -> Optional[Dict]:
        return None
    
    async def _search_component_database(self, site: str, component: str) -> Optional[Dict]:
        return None
    
    async def _search_forums(self, search: str) -> Optional[Dict]:
        return None
    
    async def _search_manufacturer_info(self, search: str) -> Optional[Dict]:
        return None
    
    def _extract_wokwi_detailed_data(self, soup, comp_data):
        pass
    
    def _extract_tutorial_data(self, data, comp_data):
        pass
    
    def _extract_arduino_detailed_data(self, data, comp_data):
        pass
    
    def _extract_component_database_data(self, data, comp_data):
        pass
    
    def _extract_forum_knowledge(self, data, comp_data):
        pass
    
    def _extract_manufacturer_data(self, data, comp_data):
        pass
    
    async def collect_all_comprehensive_data(self) -> List[ComprehensiveHardwareData]:
        """Collect comprehensive data for all hardware components"""
        all_data = []
        
        for component in HARDWARE_COMPONENTS:
            logger.info(f"Starting comprehensive collection for {component['name']}")
            
            comp_data = await self.collect_comprehensive_data(component)
            all_data.append(comp_data)
            
            # Save individual component data
            self.save_component_data(comp_data)
            
            # Rate limiting between components
            await asyncio.sleep(3)
        
        return all_data
    
    def save_component_data(self, comp_data: ComprehensiveHardwareData):
        """Save comprehensive component data"""
        filename = f"comprehensive_{comp_data.name.replace(' ', '_').replace('(', '').replace(')', '')}.json"
        filepath = RAW_DATA_DIR / filename
        
        # Convert to dict and save
        data_dict = asdict(comp_data)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data_dict, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved comprehensive data for {comp_data.name}")
    
    def cleanup(self):
        """Cleanup resources"""
        if self.driver:
            self.driver.quit()

async def main():
    """Main comprehensive data collection function"""
    logger.info("Starting comprehensive hardware data collection...")
    
    collector = ComprehensiveDataCollector()
    
    try:
        # Collect comprehensive data for all components
        all_data = await collector.collect_all_comprehensive_data()
        
        # Save master file
        master_data = [asdict(comp_data) for comp_data in all_data]
        
        with open(RAW_DATA_DIR / "comprehensive_hardware_data.json", 'w', encoding='utf-8') as f:
            json.dump(master_data, f, indent=2, ensure_ascii=False)
        
        logger.info("Comprehensive data collection completed!")
        logger.info(f"Collected data for {len(all_data)} components")
        
        # Display summary
        for comp_data in all_data:
            logger.info(f"   {comp_data.name}: {len(comp_data.pin_functions)} pin functions, "
                       f"{len(comp_data.typical_connections)} wiring examples, "
                       f"{len(comp_data.common_issues)} troubleshooting items")
        
    finally:
        collector.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
