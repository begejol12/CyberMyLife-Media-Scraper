import requests
import json
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urlparse, urljoin
import time
from bs4 import BeautifulSoup
import re

class ImageScraper:
    def __init__(self):
        self.load_config()
        
    def load_config(self):
        with open('config.json', 'r') as f:
            config = json.load(f)
            self.timeout = config['timeout']
            self.max_concurrent = config['max_concurrent_downloads']
    
    def extract_images_from_url(self, url):
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            images = []
            
            for img in soup.find_all('img'):
                src = img.get('src') or img.get('data-src') or img.get('data-lazy')
                if src:
                    full_url = urljoin(url, src)
                    if self.is_valid_image_url(full_url):
                        images.append({
                            'url': full_url,
                            'ext': self.get_extension(full_url),
                            'alt': img.get('alt', '')
                        })
            
            return {'images': images}
            
        except requests.RequestException as e:
            raise Exception(f"Failed to fetch website: {str(e)}")
    
    def is_valid_image_url(self, url):
        image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.svg']
        return any(url.lower().endswith(ext) for ext in image_extensions)
    
    def get_extension(self, url):
        ext = os.path.splitext(urlparse(url).path)[1].lower()
        return ext[1:] if ext else 'jpg'
    
    def get_next_folder_number(self):
        base_path = './scrap'
        if not os.path.exists(base_path):
            os.makedirs(base_path)
        
        counter = 1
        while os.path.exists(f'{base_path}/scrapping{counter}'):
            counter += 1
        return counter
    
    def download_single_image(self, image_data, folder_path):
        try:
            image_url = image_data['url']
            extension = image_data.get('ext', 'jpg')
            
            filename = urlparse(image_url).path.split('/')[-1]
            if not filename or '.' not in filename:
                filename = f"image_{int(time.time())}.{extension}"
            
            response = requests.get(image_url, timeout=self.timeout)
            response.raise_for_status()
            
            filepath = os.path.join(folder_path, filename)
            with open(filepath, 'wb') as f:
                f.write(response.content)
            
            return {
                'success': True,
                'filename': filename,
                'size': len(response.content),
                'url': image_url
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'url': image_data['url']
            }
    
    def download_images(self, images_data, progress_callback=None):
        folder_number = self.get_next_folder_number()
        folder_path = f'./scrap/scrapping{folder_number}'
        os.makedirs(folder_path, exist_ok=True)
        
        results = []
        total_images = len(images_data)
        
        with ThreadPoolExecutor(max_workers=self.max_concurrent) as executor:
            future_to_image = {
                executor.submit(self.download_single_image, img_data, folder_path): img_data
                for img_data in images_data
            }
            
            completed = 0
            for future in as_completed(future_to_image):
                result = future.result()
                results.append(result)
                completed += 1
                
                if progress_callback:
                    progress_callback(completed, total_images)
        
        successful = [r for r in results if r['success']]
        failed = [r for r in results if not r['success']]
        
        return {
            'folder_path': folder_path,
            'successful_downloads': successful,
            'failed_downloads': failed,
            'total_images': total_images
        }
