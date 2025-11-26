
import time
from SCRAPER.job_scraper import JobScraper
import json


def main():
    # url = 'https://uk.indeed.com/jobs?q=junior+software+engineer&l=Manchester%2C+Greater+Manchester&from=searchOnHP%2Cwhereautocomplete&vjk=dfa1aa4ef118ff5a&advn=2999229246842776' #input("Enter the job posting URL: ")
    scraper = JobScraper()

    # replace this with something that extracts all info when a user is on a search results page
    search_url = "https://uk.indeed.com/jobs?q=junior+software+engineer&l=Manchester"

    print("=" * 70)
    print("INDEED JOB SCRAPER - FULL DESCRIPTIONS")
    print("=" * 70)
    print()

    # Scrape jobs with FULL descriptions
    all_jobs = scraper.scrape_indeed_search_full(search_url)

    print("\n" + "=" * 70)
    print(f"✓ COMPLETE! Scraped {len(all_jobs)} jobs with full details")
    print("=" * 70)

    # Display full results
    for i, job in enumerate(all_jobs, 1):
        print(f"\n{'=' * 70}")
        print(f"JOB {i}/{len(all_jobs)}")
        print(f"{'=' * 70}")
        print(f"Title:       {job['title']}")
        print(f"Company:     {job['company']}")
        print(f"Location:    {job['location']}")
        print(f"Salary:      {job['salary'] or 'Not specified'}")
        print(f"Type:        {job['job_type'] or 'Not specified'}")
        print(f"URL:         {job['url']}")

        if job['benefits']:
            print(f"\nBenefits:")
            for benefit in job['benefits']:
                print(f"  • {benefit}")

        print(f"\n{'─' * 70}")
        print(f"FULL JOB DESCRIPTION ({len(job['description'])} characters):")
        print(f"{'─' * 70}")
        print(job['description'])
        print(f"{'─' * 70}")

    # Save to JSON with FULL descriptions
    output_file = 'indeed_jobs_full_descriptions.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_jobs, f, indent=2, ensure_ascii=False)

    print(f"\n{'=' * 70}")
    print(f"✓ Saved {len(all_jobs)} jobs with FULL descriptions to '{output_file}'")
    print(f"{'=' * 70}")






if __name__ == '__main__':
    main()


