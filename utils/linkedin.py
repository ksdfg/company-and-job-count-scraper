from traceback import print_exception

from selenium import webdriver
from selenium.common import StaleElementReferenceException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.firefox import GeckoDriverManager

from core.config import settings
from schemas.company import CompanyWithJobCounts, CompanyWithLinkedinSlug


def setup_driver() -> webdriver.Firefox:
    """
    Set up a Selenium WebDriver session with Firefox and log into LinkedIn using the LI_AT cookie.

    The session is set up to be headless, and the cookie is added to the session to log in to LinkedIn.
    The method returns the active WebDriver session.

    :return: A Selenium WebDriver session with Firefox and a logged-in LinkedIn session.
    :rtype: webdriver.Firefox
    """
    options = Options()
    options.add_argument("--disable-blink-features=AutomationControlled")
    # options.add_argument("--headless")

    driver = webdriver.Firefox(service=Service(GeckoDriverManager().install()), options=options)

    # Open LinkedIn and login using the cookie
    driver.get("https://www.linkedin.com/")
    driver.add_cookie({"name": "li_at", "value": settings.LI_AT_COOKIE, "domain": ".linkedin.com"})
    driver.refresh()

    # Wait for the page to load
    WebDriverWait(driver, 10).until(
        expected_conditions.visibility_of_element_located((By.CSS_SELECTOR, ".profile-card"))
    )

    return driver  # Keep this session active


def get_jobs_for_title(driver: webdriver.Firefox, original_window: str, job_title: str) -> int:
    """
    Search for job postings with a given title and return the number of postings found.

    The method takes a WebDriver session, the original window handle, and a job title as input.
    It searches for job postings with the given title, waits for the results page to load,
    extracts the number of job postings, closes the results tab, and switches back to the original tab.

    If an exception occurs during the process, the method will return 0.

    :param driver: An active WebDriver session
    :param original_window: The original window handle
    :param job_title: The job title to search for
    :return: The number of job postings found
    """
    job_count = 0

    try:
        wait = WebDriverWait(driver, 5)

        # Find and interact with the job search input field
        search_box_selector_args = (
            By.CSS_SELECTOR,
            ".org-jobs-job-search-form-module__typeahead-input.org-jobs-job-search-form-module__typeahead-input",
        )
        wait.until(expected_conditions.element_to_be_clickable(search_box_selector_args))
        search_box = driver.find_element(*search_box_selector_args)
        search_box.clear()
        search_box.send_keys(job_title)

        # Click the search button
        driver.find_element(By.CSS_SELECTOR, "[data-view-name='org-member-jobs-job-search-button']").click()

        # Wait for a new tab to open adn then switch to it
        wait.until(lambda d: len(d.window_handles) > 1)
        driver.switch_to.window(driver.window_handles[-1])

        # Wait for the results page to load
        wait.until(
            expected_conditions.presence_of_element_located((By.CSS_SELECTOR, ".jobs-search-results-list__subtitle"))
        )

        try:
            # Extract the number of job postings
            result = driver.find_element(By.CSS_SELECTOR, ".jobs-search-results-list__subtitle")
            job_count = int(result.text.split(" ")[0].replace(",", ""))
        except StaleElementReferenceException:
            # This happens if there are no matching jobs found, since the element will first be present and then disappear
            return 0
        except TimeoutException:
            return 0

    except Exception as e:
        print_exception(e)

    finally:
        # Close the results tab and switch back to the original tab
        driver.close()
        driver.switch_to.window(original_window)

        return job_count


def get_jobs(driver: webdriver.Firefox, company_handle: str, job_titles: list[str]) -> dict[str, int]:
    """
    Search for job postings on LinkedIn for a given company and job title.

    The method takes a company handle and job title as input, navigates to the company's job listings page,
    searches for the job title, waits for the results page to load, extracts the number of job postings,
    and returns the count.

    :param driver: An active WebDriver session
    :param company_handle: The LinkedIn company handle to search for job postings.
    :param job_titles: The job titles to search for.
    :return: The number of job postings found for the given company and job titles.
    """

    job_counts = {title: 0 for title in job_titles}

    try:
        wait = WebDriverWait(driver, 5)

        # Navigate to the company's job listings page
        driver.get(f"https://www.linkedin.com/company/{company_handle}/jobs")
        original_window = driver.current_window_handle

        # Wait for the page to load
        try:
            wait.until(expected_conditions.visibility_of_element_located((By.CSS_SELECTOR, "#ember34")))
        except Exception as e:
            # If this LinkedIn Page isn’t available, it's mostly because the LinkedIn slug is incorrect
            if "This LinkedIn Page isn’t available" in driver.page_source:
                return job_counts

            raise e

        # If there are no jobs or the LinkedIn slug is incorrect, return 0
        if (
            "There are no jobs right now" in driver.page_source
            or "This LinkedIn Page isn’t available" in driver.page_source
        ):
            return job_counts

        for job_title in job_titles:
            job_counts[job_title] = get_jobs_for_title(driver, original_window, job_title)

        return job_counts

    except Exception as e:
        print(f"Error searching jobs for {company_handle}:")
        print_exception(e)
        return job_counts


def enrich_company_with_job_counts(driver: webdriver.Firefox, company: CompanyWithLinkedinSlug) -> CompanyWithJobCounts:
    """
    Enrich a CompanyWithLinkedinSlug object with job counts for the company.

    The method takes a CompanyWithLinkedinSlug object and a Selenium WebDriver session as input,
    searches for job postings on LinkedIn for the given company and job titles "AI", "Engineer", and "IT",
    extracts the number of job postings for each job title,
    and returns a CompanyWithJobCounts object with the job counts.

    :param driver: A Selenium WebDriver session.
    :param company: A CompanyWithLinkedinSlug object to enrich with job counts.
    :return: A CompanyWithJobCounts object with the job counts.
    """
    # Get the job counts for the company
    results = get_jobs(driver, company.linkedin_slug, ["AI", "Engineer", "IT"])

    # Create a CompanyWithJobCounts object with the job counts
    return CompanyWithJobCounts(
        **company.model_dump(),
        ai_jobs=results["AI"],
        engineer_jobs=results["Engineer"],
        it_jobs=results["IT"],
    )


if __name__ == "__main__":
    driver = setup_driver()

    company = CompanyWithLinkedinSlug(
        company_name="Opus",
        industry="Internet",
        location="United States, Illinois",
        revenue="$1B and Over",
        employees="11-50",
        cience_details_page="https://www.cience.com/company/opus/1639153433099655092",
        linkedin_slug="google",
    )

    enriched_company = enrich_company_with_job_counts(driver, company)
    print(enriched_company)

    driver.quit()
