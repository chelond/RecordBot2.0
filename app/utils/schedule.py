import requests
from bs4 import BeautifulSoup
from PIL import Image, ImageDraw, ImageFont
import os
import json
from datetime import datetime, timedelta

# Configuration variables
FONT_PATH = os.path.join(os.path.dirname(__file__), 'fonts', 'ArialUnicodeMS.ttf')
URL = "https://recordfit63.ru/schedule/"
OUTPUT_IMAGE = "schedule.png"
CACHE_FILE = "schedule_cache.json"
CACHE_DURATION = 3600  # Cache duration in seconds (1 hour)


def fetch_html(url):
    """Fetch HTML content from URL with timeout and error handling"""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.text
    except requests.Timeout:
        print("Request timed out")
        return ""
    except requests.RequestException as e:
        print(f"Error fetching HTML: {e}")
        return ""


def get_cached_schedule(url, cache_file=CACHE_FILE, cache_duration=CACHE_DURATION):
    """Get schedule from cache or fetch new data if cache is expired"""
    if os.path.exists(cache_file):
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                cache = json.load(f)
                if datetime.now().timestamp() - cache['timestamp'] < cache_duration:
                    return cache['data']
        except (json.JSONDecodeError, KeyError):
            pass

    html_content = fetch_html(url)
    schedule = extract_schedule(html_content)

    try:
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump({
                'timestamp': datetime.now().timestamp(),
                'data': schedule
            }, f, ensure_ascii=False)
    except Exception as e:
        print(f"Error saving cache: {e}")

    return schedule


def extract_schedule(html_content):
    """Extract schedule data from HTML content using optimized selectors"""
    if not html_content:
        return []

    soup = BeautifulSoup(html_content, "lxml")
    schedule = []

    days = soup.select("div.col")
    for day in days:
        date_div = day.select_one("div.cel.date")
        if not date_div:
            continue

        date = date_div.text.strip()
        events = day.select("div[class*='cel class'], div[class*='ct-']")

        for event in events:
            if "cel not" in event.get("class", []):
                continue

            schedule.append({
                "date": date,
                "time": event.select_one("div.time").text.strip() if event.select_one("div.time") else "N/A",
                "lesson": event.select_one("span.lesson").text.strip() if event.select_one("span.lesson") else "N/A",
                "trainer": event.select_one("span.name").text.strip() if event.select_one("span.name") else "N/A",
                "room": event.select_one("span.number").text.strip() if event.select_one("span.number") else "N/A",
            })

    return schedule


def create_image(schedule, output_file):
    """Generate image with schedule using optimized drawing"""
    try:
        # Cache fonts
        fonts = {
            'regular': ImageFont.truetype(FONT_PATH, 18),
            'header': ImageFont.truetype(FONT_PATH, 22),
            'title': ImageFont.truetype(FONT_PATH, 28)
        }

        # Calculate dynamic image dimensions
        entries_count = len(schedule)
        estimated_height = 200 + (entries_count * 50)  # Base height + entries
        img_height = min(max(estimated_height, 800), 10000)  # Dynamic height with limits
        img_width = 1200

        # Image settings
        padding = 50
        line_spacing = 40
        column_spacing = [150, 350, 550, 800]

        # Colors
        bg_color = (245, 245, 245)
        header_color = (30, 30, 30)
        text_color = (60, 60, 60)
        line_color = (200, 200, 200)

        # Create image
        img = Image.new('RGB', (img_width, 2000), color=bg_color)
        draw = ImageDraw.Draw(img)

        # Initial coordinates
        x, y = padding, padding

        # Add title
        draw.text((x, y), "Расписание тренировок на неделю", font=fonts['title'], fill=header_color)
        y += 60

        # Column headers
        headers = ["Время", "Занятие", "Тренер", "Кабинет"]
        for i, header in enumerate(headers):
            draw.text((x + column_spacing[i], y), header, font=fonts['header'], fill=header_color)
        y += line_spacing

        # Header underline
        draw.line((padding, y, img_width - padding, y), fill=line_color, width=2)
        y += 20

        current_date = None
        for item in schedule:
            # Date display
            if item['date'] != current_date:
                current_date = item['date']
                y += 20
                draw.text((x, y), f"Дата: {current_date}", font=fonts['header'], fill=header_color)
                y += line_spacing

            # Data display
            values = [item['time'], item['lesson'], item['trainer'], item['room']]
            for i, value in enumerate(values):
                draw.text((x + column_spacing[i], y), value, font=fonts['regular'], fill=text_color)
            y += line_spacing

            # Separator line
            draw.line((padding, y, img_width - padding, y), fill=line_color, width=1)
            y += 10



        img.save(output_file)
        print(f"Image saved to: {output_file}")
    except Exception as e:
        print(f"Error creating image: {e}")


def main():
    """Main execution function with error handling"""
    try:
        # Get schedule with caching
        schedule = get_cached_schedule(URL)

        if schedule:
            create_image(schedule, OUTPUT_IMAGE)
        else:
            print("Failed to retrieve schedule data")

    except Exception as e:
        print(f"An error occurred: {e}")


async def admin_create_schedule():
    main()