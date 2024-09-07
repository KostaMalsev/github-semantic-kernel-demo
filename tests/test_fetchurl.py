import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fetchurl import get_content_from_url



if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python run_url_content.py <url>")
        sys.exit(1)
    
    url = sys.argv[1]

    content = get_content_from_url(url,'html')
    print(content)
