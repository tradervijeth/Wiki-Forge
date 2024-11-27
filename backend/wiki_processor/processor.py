# backend/wiki_processor/processor.py
import wikipediaapi
import pandas as pd
from typing import List, Dict, Optional
from pathlib import Path
import re
from datetime import datetime
import logging

class WikiDatasetProcessor:
    def __init__(self, language: str = 'en'):
        """Initialize the Wikipedia processor with specified language."""
        self.wiki = wikipediaapi.Wikipedia(
            language=language,
            extract_format=wikipediaapi.ExtractFormat.WIKI,
            user_agent='WikiForge/1.0'
        )
        self.logger = self._setup_logger()
        
    def _setup_logger(self) -> logging.Logger:
        """Set up logging configuration."""
        logger = logging.getLogger('WikiProcessor')
        logger.setLevel(logging.INFO)
        
        # Create handlers if they don't exist
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            
        return logger

    def fetch_article(self, title: str) -> Optional[Dict]:
        """
        Fetch a single Wikipedia article and extract its content.
        
        Args:
            title (str): The title of the Wikipedia article to fetch
            
        Returns:
            Optional[Dict]: Article data or None if fetch fails
        """
        try:
            page = self.wiki.page(title)
            if not page.exists():
                self.logger.warning(f"Page '{title}' does not exist")
                return None
            
            return {
                'title': page.title,
                'text': page.text,
                'summary': page.summary,
                'url': page.fullurl,
                'categories': list(page.categories.keys()),
                'references': len(page.references),
                'processed_date': datetime.now().isoformat()
            }
        except Exception as e:
            self.logger.error(f"Error fetching article '{title}': {str(e)}")
            return None

    def clean_text(self, text: str) -> str:
        """
        Clean and normalize text content.
        
        Args:
            text (str): Raw text content to clean
            
        Returns:
            str: Cleaned text
        """
        if not text:
            return ""
            
        # Remove citations and brackets
        text = re.sub(r'\[\d+\]', '', text)
        text = re.sub(r'\{.*?\}', '', text)
        
        # Remove multiple spaces and newlines
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s.,!?-]', '', text)
        
        return text.strip()

    def process_articles(self, titles: List[str], output_path: str) -> pd.DataFrame:
        """
        Process multiple articles and save to CSV/JSON.
        
        Args:
            titles (List[str]): List of article titles to process
            output_path (str): Path to save the processed data
            
        Returns:
            pd.DataFrame: Processed articles data
        """
        processed_data = []
        
        for title in titles:
            self.logger.info(f"Processing article: {title}")
            article_data = self.fetch_article(title)
            
            if article_data:
                # Clean the text content
                article_data['clean_text'] = self.clean_text(article_data['text'])
                article_data['clean_summary'] = self.clean_text(article_data['summary'])
                processed_data.append(article_data)
        
        if not processed_data:
            self.logger.warning("No articles were successfully processed")
            return pd.DataFrame()
            
        # Convert to DataFrame
        df = pd.DataFrame(processed_data)
        
        # Create output directory if it doesn't exist
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Save processed data
        df.to_csv(output_path.with_suffix('.csv'), index=False)
        df.to_json(output_path.with_suffix('.json'), orient='records')
        
        self.logger.info(f"Processed {len(processed_data)} articles successfully")
        return df

    def get_article_statistics(self, df: pd.DataFrame) -> Dict:
        """
        Calculate statistics about the processed articles.
        
        Args:
            df (pd.DataFrame): Processed articles DataFrame
            
        Returns:
            Dict: Statistical information about the articles
        """
        if df.empty:
            return {
                'total_articles': 0,
                'avg_text_length': 0,
                'avg_summary_length': 0,
                'total_references': 0,
                'unique_categories': 0,
                'processing_date_range': [None, None]
            }
            
        return {
            'total_articles': len(df),
            'avg_text_length': int(df['clean_text'].str.len().mean()),
            'avg_summary_length': int(df['clean_summary'].str.len().mean()),
            'total_references': int(df['references'].sum()),
            'unique_categories': len(set([cat for cats in df['categories'] for cat in cats])),
            'processing_date_range': [
                df['processed_date'].min(),
                df['processed_date'].max()
            ]
        }