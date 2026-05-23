import smtplib
import json
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime


class NewsEmailSender:
    def __init__(self):
        self.sender_email = os.getenv('SENDER_EMAIL')
        self.sender_password = os.getenv('SENDER_PASSWORD')
        self.recipient_email = os.getenv('RECIPIENT_EMAIL')
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', 587))
    
    def validate_config(self) -> bool:
        """Validate email configuration"""
        if not all([self.sender_email, self.sender_password, self.recipient_email]):
            print("❌ Missing required email configuration")
            print(f"SENDER_EMAIL: {self.sender_email}")
            print(f"RECIPIENT_EMAIL: {self.recipient_email}")
            print(f"SENDER_PASSWORD: {'***' if self.sender_password else 'NOT SET'}")
            return False
        return True
    
    def load_news(self, filename: str = 'daily_news.json') -> dict:
        """Load news from JSON file"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"❌ News file not found: {filename}")
            return {'count': 0, 'news': []}
    
    def generate_html_email(self, news_data: dict) -> str:
        """Generate HTML email content"""
        today = datetime.now().strftime('%Y年%m月%d日')
        news_count = news_data.get('count', 0)
        news_list = news_data.get('news', [])
        
        html = f"""
        <html>
            <head>
                <meta charset="utf-8">
                <style>
                    body {{ 
                        font-family: 'Segoe UI', 'Microsoft YaHei', Arial, sans-serif; 
                        color: #333; 
                        line-height: 1.6;
                        margin: 0;
                        padding: 0;
                        background-color: #f5f5f5;
                    }}
                    .container {{ 
                        max-width: 800px; 
                        margin: 0 auto; 
                        padding: 20px; 
                        background-color: #ffffff;
                    }}
                    .header {{ 
                        background: linear-gradient(135deg, #76b900 0%, #1db942 100%); 
                        color: white; 
                        padding: 30px; 
                        border-radius: 8px 8px 0 0;
                        margin: -20px -20px 30px -20px;
                    }}
                    .header h1 {{ 
                        margin: 0; 
                        font-size: 28px;
                        font-weight: bold;
                    }}
                    .header p {{ 
                        margin: 10px 0 0 0; 
                        font-size: 14px; 
                        opacity: 0.9; 
                    }}
                    .stats {{ 
                        background: #f0f0f0; 
                        padding: 15px; 
                        border-radius: 4px; 
                        margin-bottom: 20px; 
                        text-align: center;
                    }}
                    .stats p {{ 
                        margin: 0; 
                        font-size: 16px; 
                        color: #1db942; 
                        font-weight: bold; 
                    }}
                    .news-item {{ 
                        background: #f9f9f9; 
                        border-left: 4px solid #76b900; 
                        padding: 15px; 
                        margin-bottom: 15px; 
                        border-radius: 4px;
                    }}
                    .news-item h3 {{ 
                        margin: 0 0 10px 0; 
                        color: #1db942; 
                        font-size: 16px;
                        line-height: 1.4;
                    }}
                    .news-item p {{ 
                        margin: 0 0 10px 0; 
                        color: #666; 
                        font-size: 14px; 
                        line-height: 1.6; 
                    }}
                    .news-item .source {{ 
                        color: #999; 
                        font-size: 12px; 
                    }}
                    .news-item a {{ 
                        color: #1db942; 
                        text-decoration: none;
                        word-break: break-all;
                    }}
                    .news-item a:hover {{ 
                        text-decoration: underline; 
                    }}
                    .footer {{ 
                        text-align: center; 
                        color: #999; 
                        font-size: 12px; 
                        margin-top: 30px; 
                        padding-top: 20px; 
                        border-top: 1px solid #eee; 
                    }}
                    .divider {{ 
                        height: 1px; 
                        background-color: #eee; 
                        margin: 15px 0;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>📰 NVIDIA AI服务器供应链日报</h1>
                        <p>每日精选新闻汇总 · {today}</p>
                    </div>
                    
                    <div class="stats">
                        <p>今日共收集 <strong>{news_count}</strong> 条相关新闻</p>
                    </div>
        """
        
        # Add news items
        for idx, news in enumerate(news_list, 1):
            title = news.get('title', '未知标题')
            description = news.get('description', '')
            url = news.get('url', '#')
            source = news.get('source', {}).get('name', '未知来源')
            
            html += f"""
                    <div class="news-item">
                        <h3>{idx}. {title}</h3>
                        <p>{description}</p>
                        <div class="divider"></div>
                        <p style="margin: 0;">
                            <a href="{url}" target="_blank">📖 阅读全文 →</a>
                            <span class="source" style="margin-left: 20px;">来源: {source}</span>
                        </p>
                    </div>
            """
        
        html += """
                    <div class="footer">
                        <p>这是一份自动生成的日报，由GitHub Actions每日定时发送。</p>
                        <p>如有任何问题，请访问仓库进行反馈。</p>
                        <p style="margin: 10px 0 0 0; opacity: 0.7;">Daily NVIDIA AI Server Supply Chain News Digest</p>
                    </div>
                </div>
            </body>
        </html>
        """
        
        return html
    
    def send_email(self, subject: str, html_content: str):
        """Send email with HTML content"""
        if not self.validate_config():
            raise ValueError("Email configuration is incomplete")
        
        try:
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = self.sender_email
            message["To"] = self.recipient_email
            
            # Add HTML part
            part = MIMEText(html_content, "html", "utf-8")
            message.attach(part)
            
            # Connect to SMTP server and send
            print(f"Connecting to {self.smtp_server}:{self.smtp_port}...")
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.sendmail(self.sender_email, self.recipient_email, message.as_string())
            
            print(f"✅ Email sent successfully to {self.recipient_email}")
        
        except Exception as e:
            print(f"❌ Error sending email: {e}")
            raise


if __name__ == '__main__':
    sender = NewsEmailSender()
    news_data = sender.load_news()
    
    if news_data.get('count', 0) > 0:
        today = datetime.now().strftime('%Y年%m月%d日')
        subject = f"📰 NVIDIA AI服务器供应链日报 - {today}"
        html_content = sender.generate_html_email(news_data)
        sender.send_email(subject, html_content)
        print("✅ Daily digest email sent!")
    else:
        print("⚠️ No news found to send")
