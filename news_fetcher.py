import requests
import json
import feedparser
from datetime import datetime
from typing import List, Dict
import hashlib


class NVIDIANewsFetcher:
    def __init__(self):
        self.news_list = []
        
        # NVIDIA and AI-related keywords
        self.nvidia_keywords = [
            'NVIDIA', 'nvidia', '英伟达',
            'GPU', 'AI', 'artificial intelligence',
            'H100', 'A100', 'L40', 'H200',
            'data center', '数据中心',
            'chip', '芯片', 'semiconductor',
            'machine learning', 'deep learning',
            'transformer', 'LLM'
        ]
        
        # China-listed companies in NVIDIA supply chain
        self.china_companies = {
            '芯片制造': ['中芯国际', 'SMIC', 'Semiconductor Manufacturing International', 
                       '安集微电子', '晶方科技', '长川科技', '华峰测控', 
                       '兆易创新', 'GigaDevice', '韦尔股份'],
            '散热冷却': ['九州风神', 'Deepcool', '法拉电子'],
            'PCB材料': ['生益科技', '金安国纪', '上海新昇'],
            'AI平台': ['浪潮信息', 'Inspur', '中科曙光', 'Sugon', '商汤科技', 'SenseTime'],
            '互联网': ['华为', 'Huawei', '阿里', 'Alibaba', '腾讯', 'Tencent',
                     '百度', 'Baidu', '字节跳动', 'ByteDance', 'JiuZhou']
        }
        
        # RSS news sources
        self.rss_feeds = [
            'https://feeds.bloomberg.com/markets/news.rss',
            'https://feeds.cnbc.com/news/',
            'https://feeds.reuters.com/reuters/technologyNews',
            'https://feeds.bloomberg.com/technology/news.rss',
        ]
    
    def is_relevant_news(self, title: str, description: str = '') -> bool:
        """Check if news is relevant to NVIDIA supply chain"""
        text = (title + ' ' + description).lower()
        
        # Check for NVIDIA or AI keywords
        nvidia_match = any(kw.lower() in text for kw in self.nvidia_keywords)
        
        # Check for China supply chain companies
        company_match = False
        for category, companies in self.china_companies.items():
            if any(comp.lower() in text for comp in companies):
                company_match = True
                break
        
        return nvidia_match or company_match
    
    def fetch_from_rss(self) -> List[Dict]:
        """Fetch news from RSS feeds"""
        articles = []
        
        for feed_url in self.rss_feeds:
            try:
                print(f"Fetching from: {feed_url}")
                feed = feedparser.parse(feed_url)
                
                for entry in feed.entries[:30]:
                    title = entry.get('title', '')
                    summary = entry.get('summary', '')
                    link = entry.get('link', '')
                    published = entry.get('published', datetime.now().isoformat())
                    
                    # Check relevance
                    if self.is_relevant_news(title, summary):
                        articles.append({
                            'title': title,
                            'description': summary[:250] if summary else '',
                            'url': link,
                            'publishedAt': published,
                            'source': {'name': feed.feed.get('title', 'RSS Feed')},
                            'hash': hashlib.md5(title.encode()).hexdigest()
                        })
            
            except Exception as e:
                print(f"Error fetching from {feed_url}: {e}")
                continue
        
        print(f"Fetched {len(articles)} articles from RSS feeds")
        return articles
    
    def deduplicate_news(self, news_list: List[Dict]) -> List[Dict]:
        """Remove duplicate news items"""
        seen_hashes = set()
        unique = []
        
        for item in news_list:
            item_hash = item.get('hash') or hashlib.md5(item.get('title', '').encode()).hexdigest()
            
            if item_hash not in seen_hashes:
                seen_hashes.add(item_hash)
                unique.append(item)
        
        return unique
    
    def sort_news(self, news_list: List[Dict]) -> List[Dict]:
        """Sort news by publish date (newest first)"""
        try:
            return sorted(
                news_list,
                key=lambda x: x.get('publishedAt', ''),
                reverse=True
            )
        except:
            return news_list
    
    def fetch_all_news(self, max_items: int = 20) -> List[Dict]:
        """Fetch and process all news"""
        print(f"Fetching NVIDIA supply chain news...")
        
        # Fetch from RSS
        self.news_list.extend(self.fetch_from_rss())
        
        # Deduplicate
        self.news_list = self.deduplicate_news(self.news_list)
        
        # Sort by date
        self.news_list = self.sort_news(self.news_list)
        
        # Limit to max items
        self.news_list = self.news_list[:max_items]
        
        print(f"Total {len(self.news_list)} unique news items retrieved")
        return self.news_list
    
    def save_to_file(self, filename: str = 'daily_news.json'):
        """Save news to JSON file"""
        output_data = {
            'timestamp': datetime.now().isoformat(),
            'count': len(self.news_list),
            'news': self.news_list
        }
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, ensure_ascii=False, indent=2)
            print(f"✅ News saved to {filename}")
        except Exception as e:
            print(f"❌ Error saving news: {e}")


if __name__ == '__main__':
    print("=" * 60)
    print("NVIDIA AI Server Supply Chain News Fetcher")
    print("=" * 60)
    
    fetcher = NVIDIANewsFetcher()
    fetcher.fetch_all_news(max_items=20)
    fetcher.save_to_file()
    
    print("=" * 60)
    print(f"Fetched {len(fetcher.news_list)} news items")
    print("=" * 60)
