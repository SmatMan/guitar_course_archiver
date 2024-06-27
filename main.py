from playwright.sync_api import sync_playwright
from config import email, password
import yt_dlp
import tempfile
import re
import json
from http.cookiejar import Cookie


global cookies
cookies = []
    

def response_handler(response):
    if "oembed" in response.url:
        iframe = response.json()['html']
        id = extract_vimeo_id(iframe)
        url = f"https://player.vimeo.com/video/{id}"
        download(url, cookies)
        
        
def extract_vimeo_id(url):
    pattern = r'https://player\.vimeo\.com/video/(\d+)'
    match = re.search(pattern, url)
    if match:
        return match.group(1)
    return None

def download(url, cookies):
    yt_dlp.utils.std_headers['Referer'] = "https://www.justinguitar.com"
    ydl_opts = {
        'referer': "https://www.justinguitar.com",
    }   
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        for key, value in cookies.items():
            ydl.cookiejar.set_cookie(Cookie(name=key, value=value, version=0, port=None, domain='.justinguitar.com', path='/', secure=True, expires=None, discard=False, comment=None, comment_url=None, rest={'HttpOnly': None}, domain_initial_dot=True, port_specified=False, domain_specified=True, path_specified=False))
        ydl.download([url])

    


url = "https://www.justinguitar.com/modules/major-scale-theory-key-signatures"
baseurl = "https://www.justinguitar.com"
login_url = "https://www.justinguitar.com/users/sign_in"

if __name__ == "__main__":
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=1000)
        context = browser.new_context()
        page = context.new_page()
        page.goto(url=login_url)

        usernameBox = page.locator(".auth__input input").first
        usernameBox.fill(email)

        passwordBox = page.locator(".auth__input input").last
        passwordBox.fill(password)

        loginButton = page.locator(".auth__btn")
        loginButton.click()
        
        page.wait_for_timeout(1000)
        page.goto(url=url)
        
        page.locator(".close-button").click()
        print("Accepted Cookies")

        rawLessons = page.locator(".group-lessons").first.locator(".group-lesson")
        
        page.on("response", response_handler)

        lessons = []
        for lesson in range(rawLessons.count()+2): 
            cookies = {cookie['name']: cookie['value'] for cookie in context.cookies()}
            
            print(f"Page {lesson}")
            lesson = rawLessons.nth(lesson).locator(".group-lesson__text").click()
            
            lessonTitle = page.locator(".video-swoosh__title h1").first.inner_text().title()
            print(lessonTitle)
            
            url = page.url

            # y = yt_dlp.YoutubeDL(url)
            



            # # print window.playerConfig attribute
            # print(page.evaluate("window.playerConfig"))

            
            # if page.locator("ytp-title-text").count() > 0:
            #     print("Youtube Video")
            # elif page.locator(".vp-video").count() > 0:
            #     print("Vimeo Video")
            #     video = page.locator(".vp-video").first
            #     video.click()
            # else:
            #     print("No Video")
            #     print(page.url)

            page.go_back()
            


        page.wait_for_timeout(5000)
        browser.close()