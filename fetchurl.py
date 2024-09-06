import requests
from bs4 import BeautifulSoup
from typing import Optional
from urllib.parse import urljoin




def get_content_from_url(url: str, content_type: str = 'html', max_length: Optional[int] = None) -> str:
    """
    Fetch and return the content from a given URL.

    Args:
    url (str): The URL to fetch content from.
    content_type (str): Type of content to return - 'html' for full HTML, 'text' for text only.
    max_length (Optional[int]): Maximum number of characters to return. If None, return all content.

    Returns:
    str: The content of the webpage, or an error message.
    """

    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/113.0.0.0 Safari/537.36 Edg/113.0.1774.35"
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # Raises an HTTPError for bad responses
        soup = BeautifulSoup(response.text, 'html.parser')
        
        if content_type == 'html':
            content = str(soup)
        elif content_type == 'text':
            content = soup.get_text(strip=True)
        else:
            raise ValueError("Invalid content_type. Use 'html' or 'text'.")

        if max_length is not None:
            content = content[:max_length]

        return content

    except requests.RequestException as e:
        error_msg = f"Failed to retrieve content from {url}. Error: {str(e)}"
        print(error_msg)
        return error_msg
    except ValueError as e:
        print(str(e))
        return str(e)


def extract_image_urls(url):
    """
    Extracts all image URLs from the given HTML content.
    
    Args:
    html_content (str): The HTML content to parse.
    base_url (str): The base URL of the page, used to convert relative URLs to absolute.
    
    Returns:
    list: A list of absolute URLs of all images found in the HTML.
    """

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/113.0.0.0 Safari/537.36 Edg/113.0.1774.35"
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # Raises an HTTPError for bad responses

    except requests.RequestException as e:
        error_msg = f"Failed to retrieve content from {url}. Error: {str(e)}"
        print(error_msg)
        return error_msg
    except ValueError as e:
        print(str(e))
        return str(e)


    soup = BeautifulSoup(response.text, 'html.parser')
    img_tags = soup.find_all('img')
    
    urls = []
    for img in img_tags:
        # Get the 'src' attribute of the img tag
        src = img.get('src')
        if src:
            # Make the URL absolute by joining it with the base URL
            absolute_url = src #urljoin(base_url, src)
            urls.append(absolute_url)
    
    return urls