import undetected_chromedriver as uc
from bs4 import BeautifulSoup
import time
import random


class JobScraper:
    def __init__(self):
        self.driver = None

    def _get_driver(self):
        """Initialize undetected Chrome driver"""
        options = uc.ChromeOptions()
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--no-sandbox')
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--start-maximized')

        driver = uc.Chrome(options=options, version_main=141, use_subprocess=True)

        driver.execute_cdp_cmd('Network.setUserAgentOverride', {
            "userAgent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36'
        })

        return driver

    def scrape_indeed_search_full(self, search_url, max_jobs=10):
        """
        Scrape search results AND full details for each job by visiting each posting

        Args:
            search_url: The Indeed search URL
            max_jobs: Maximum number of jobs to scrape in detail

        Returns:
            List of complete job dictionaries with full descriptions
        """
        print("=" * 70)
        print("SCRAPING INDEED JOBS WITH FULL DESCRIPTIONS")
        print("=" * 70)

        all_jobs = []

        try:
            # Initialize driver once for the entire session
            print("\nInitializing browser...")
            self.driver = self._get_driver()

            # Load search results page
            print(f"Loading search results: {search_url}")
            self.driver.get(search_url)
            time.sleep(random.uniform(4, 6))

            # Check for CAPTCHA
            if 'cloudflare' in self.driver.page_source.lower() or 'captcha' in self.driver.page_source.lower():
                print("⚠️ CAPTCHA detected. Please solve it and press Enter...")
                # input()

            # Scroll to load all jobs
            print("Scrolling to load all job listings...")
            self._scroll_page()

            # Parse the search page
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')

            # Find all job cards
            job_cards = soup.find_all('div', class_='job_seen_beacon')
            if not job_cards:
                job_cards = soup.find_all('td', class_='resultContent')
            if not job_cards:
                job_cards = soup.find_all('div', class_='jobsearch-SerpJobCard')

            print(f"✓ Found {len(job_cards)} jobs on search page")
            print(f"Will scrape full details for {min(len(job_cards), max_jobs)} jobs\n")

            # Limit to max_jobs
            job_cards = job_cards[:max_jobs]

            # Process each job card
            for i, card in enumerate(job_cards, 1):
                print(f"\n{'─' * 70}")
                print(f"Processing Job {i}/{len(job_cards)}")
                print(f"{'─' * 70}")

                # Get basic info and URL from the card
                job_url = self._extract_job_url(card)

                if not job_url:
                    print("✗ Could not extract job URL, skipping...")
                    continue

                print(f"Job URL: {job_url}")

                # Navigate to the job posting page
                print("Loading full job posting...")
                self.driver.get(job_url)
                time.sleep(random.uniform(3, 5))

                # Parse the full job page
                job_soup = BeautifulSoup(self.driver.page_source, 'html.parser')
                job_data = self._parse_indeed_full_page(job_soup, job_url)

                if job_data and job_data['description']:
                    all_jobs.append(job_data)
                    print(f"✓ SUCCESS: {job_data['title']}")
                    print(f"  Company: {job_data['company']}")
                    print(f"  Location: {job_data['location']}")
                    print(f"  Salary: {job_data['salary'] or 'Not specified'}")
                    print(f"  Description: {len(job_data['description'])} characters")

                    # Show a preview of the description
                    desc_preview = job_data['description'][:200].replace('\n', ' ')
                    print(f"  Preview: {desc_preview}...")
                else:
                    print("✗ Failed to extract job details")

                # Polite delay before next job
                if i < len(job_cards):
                    delay = random.uniform(4, 8)
                    print(f"\n⏳ Waiting {delay:.1f} seconds before next job...")
                    time.sleep(delay)

        except Exception as e:
            print(f"\n❌ Error during scraping: {e}")
            import traceback
            traceback.print_exc()

        finally:
            if self.driver:
                print("\nClosing browser...")
                self.driver.quit()

        return all_jobs

    def _extract_job_url(self, card):
        """Extract job URL from a job card"""
        try:
            # Try to find the job link
            link = card.find('a', class_='jcs-JobTitle')
            if not link:
                title_h2 = card.find('h2', class_='jobTitle')
                if title_h2:
                    link = title_h2.find('a')

            if link and 'href' in link.attrs:
                href = link['href']

                # Build full URL
                if href.startswith('http'):
                    full_url = href
                elif href.startswith('/'):
                    full_url = f"https://uk.indeed.com{href}"
                else:
                    return None

                # Clean URL - extract job key
                if 'jk=' in full_url:
                    job_key = full_url.split('jk=')[1].split('&')[0]
                    full_url = f"https://uk.indeed.com/viewjob?jk={job_key}"

                return full_url
        except:
            return None

        return None

    def _scroll_page(self):
        """Scroll page to load lazy-loaded content"""
        try:
            for _ in range(3):
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)

            self.driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(1)
        except:
            pass

    def _parse_indeed_full_page(self, soup, url):
        """Parse COMPLETE job details from the full job posting page"""
        try:
            job_data = {
                'title': 'Unknown',
                'company': 'Unknown',
                'location': 'Unknown',
                'salary': None,
                'job_type': None,
                'benefits': [],
                'description': '',
                'url': url
            }

            # ===== JOB TITLE =====
            title = soup.find('h1', class_='jobsearch-JobInfoHeader-title')
            if not title:
                title = soup.find('h1', {'data-testid': 'jobsearch-JobInfoHeader-title'})
            if not title:
                title = soup.find('h2', class_='jobsearch-JobInfoHeader-title')
            if not title:
                title = soup.find('span', class_='jobsearch-JobInfoHeader-title')
            if title:
                job_data['title'] = title.get_text(strip=True)

            # ===== COMPANY NAME =====
            company = soup.find('div', {'data-company-name': True})
            if company:
                job_data['company'] = company.get('data-company-name')

            if job_data['company'] == 'Unknown':
                company = soup.find('a', {'data-testid': 'inlineHeader-companyName'})
                if not company:
                    company = soup.find('span', {'data-testid': 'inlineHeader-companyName'})
                if not company:
                    company = soup.find('div', {'data-testid': 'inlineHeader-companyName'})
                if not company:
                    company = soup.find('span', class_='css-1h7lukg')
                if company:
                    job_data['company'] = company.get_text(strip=True)

            # ===== LOCATION =====
            location = soup.find('div', {'data-testid': 'job-location'})
            if not location:
                location = soup.find('div', {'data-testid': 'inlineHeader-companyLocation'})
            if not location:
                location = soup.find('div', {'data-testid': 'jobLocationText'})
            if location:
                job_data['location'] = location.get_text(strip=True)

            # ===== SALARY =====
            salary_container = soup.find('div', {'id': 'salaryInfoAndJobType'})
            if salary_container:
                # Look for salary within the container
                salary_text = salary_container.get_text(strip=True)
                if '£' in salary_text or '$' in salary_text:
                    job_data['salary'] = salary_text

            if not job_data['salary']:
                salary = soup.find('div', {'data-testid': 'jobsearch-JobMetadataHeader-salary'})
                if not salary:
                    salary = soup.find('span', class_='salary')
                if salary:
                    job_data['salary'] = salary.get_text(strip=True)

            # ===== JOB TYPE (Full-time, Part-time, etc) =====
            if salary_container:
                text = salary_container.get_text(strip=True)
                for jtype in ['Full-time', 'Part-time', 'Contract', 'Temporary', 'Permanent', 'Internship']:
                    if jtype in text:
                        job_data['job_type'] = jtype
                        break

            # ===== BENEFITS (from the pulled benefits section) =====
            benefits_section = soup.find('div', {'id': 'benefits'})
            if benefits_section:
                benefit_items = benefits_section.find_all('li')
                for item in benefit_items:
                    benefit = item.get_text(strip=True)
                    if benefit:
                        job_data['benefits'].append(benefit)

            # Alternative benefits location
            if not job_data['benefits']:
                benefits_text = soup.find_all('div', class_='jobsearch-JobMetadataHeader-item')
                for item in benefits_text:
                    text = item.get_text(strip=True)
                    if any(b in text.lower() for b in
                           ['parking', 'pension', 'insurance', 'dress', 'work from home', 'cycle']):
                        job_data['benefits'].append(text)

            # ===== FULL JOB DESCRIPTION =====
            # This is the most important part!
            desc = soup.find('div', {'id': 'jobDescriptionText'})
            if not desc:
                desc = soup.find('div', class_='jobsearch-jobDescriptionText')
            if not desc:
                desc = soup.find('div', {'data-testid': 'jobsearch-JobComponent-description'})
            if not desc:
                # Last resort - look for any div with a lot of text
                all_divs = soup.find_all('div', class_=lambda x: x and 'description' in x.lower())
                if all_divs:
                    desc = all_divs[0]

            if desc:
                # Get the FULL text content
                job_data['description'] = desc.get_text(separator='\n', strip=True)

                # Remove excessive newlines
                while '\n\n\n' in job_data['description']:
                    job_data['description'] = job_data['description'].replace('\n\n\n', '\n\n')
            else:
                # If we still can't find it, try getting all text from the page
                print("⚠️ Warning: Could not find description with normal selectors")
                job_data['description'] = "Description not found"

            return job_data

        except Exception as e:
            print(f"Error parsing job page: {e}")
            import traceback
            traceback.print_exc()
            return None