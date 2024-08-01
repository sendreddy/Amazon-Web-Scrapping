#!/usr/bin/env python3
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from collections import defaultdict
import time

# Function to initialize the Selenium webdriver
def init_driver():
    driver = webdriver.Chrome()  # You may need to download and specify the path to your chromedriver.exe
    return driver

# Function to scrape reviews from the product page
def scrape_reviews(driver, product_url):
    driver.get(product_url)

    try:
        # Click on the link to see all reviews
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "acrCustomerReviewLink"))
        ).click()

        # Click on the "See more reviews" link to load all reviews
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//a[@data-hook="see-all-reviews-link-foot"]'))
        ).click()

        # Wait for the reviews to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//div[@data-hook="review"]'))
        )

        # Find and extract review elements
        reviews = driver.find_elements(By.XPATH, '//div[@data-hook="review"]')

        review_data = []
        for review in reviews:
            try:
                # Find the reviewer's profile link element
                # profile_user = review.find_element(By.XPATH, '//div[@data-hook="review"]')
                profile_link_element = review.find_element(By.XPATH, '//*[@class="a-profile"]')

                # Get reviewer's name and profile URL
                reviewer_name = review.find_element(By.XPATH, './/span[@class="a-profile-name"]').text
                profile_url = profile_link_element.get_attribute('href')
                profile_ID = review.get_attribute('id')

                print(reviewer_name)
                print(profile_ID)

                # Store reviewer name and profile URL in a dictionary
                reviewer_data = {'reviewer_name': reviewer_name, 'profile_url': profile_url, 'ID': profile_ID}
                review_data.append(reviewer_data)

            except Exception as e:
                print(f"Error extracting reviewer profile link: {str(e)}")
                continue

        return review_data

    except Exception as e:
        print(f"Error: {str(e)}")
        return []


# Function to scrape the profile of each reviewer
def scrape_reviewer_profiles(driver, review_data):
    reviewer_profiles = defaultdict(dict)
    total_score = 0
    count = 0

    for review in review_data:
        reviewer_name = review['reviewer_name']
        user_ID = review['ID']
        profile_xpath = f'//*[@id="customer_review-{user_ID}"]/div[1]/a'

        try:
            WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, profile_xpath))
            ).click()

            try:
                # Initialize a dictionary to store the star ratings of all reviews
                star_counts = {'1': 0, '2': 0, '3': 0, '4': 0, '5': 0}

                # Find all elements by XPath
                elements = driver.find_elements(By.XPATH, '//span[@class="a-icon-alt"]')

                # Iterate through each element
                for element in elements:
                    # Get the text of each element
                    text = element.text

                    # Check if the text is a star rating
                    if 'out of 5 stars' in text:
                        # Extract the star rating and update the count
                        star_rating = text.split()[0]
                        star_counts[star_rating] += 1
                    else:
                        continue

                # Determine if the reviewer is biased (majority of ratings are 5 stars or 1 star)
                total_reviews = sum(star_counts.values())
                if total_reviews > 0 and (star_counts['5'] > total_reviews / 2 or star_counts['1'] > total_reviews / 2):
                    print(f"{reviewer_name} is biased.")
                else:
                    print(f"{reviewer_name} is not biased.")
                    # If the reviewer is not biased and star_rating is not None, add their rating to the total score and increment the count
                    if star_rating is not None:
                        total_score += int(star_rating) * star_counts[star_rating]
                        count += star_counts[star_rating]

            except Exception as e:
                print("Error:", str(e))

            driver.back()

        except Exception as e:
            print("Error:", str(e))

    # Calculate and print the average score given by non-biased reviewers
    if count > 0:
        average_score = total_score / count
        print(f"The average score given by non-biased reviewers is {average_score:.2f}.")

    return reviewer_profiles





def main():
    product_url = "https://www.amazon.com/Bose-QuietComfort-Cancelling-Headphones-Bluetooth/dp/B0CCZ26B5V/ref=sr_1_1_sspa?crid=29N2JVXYBS354&keywords=bose%2Bheadphones&qid=1699919994&sprefix=bose%2Bheadphone%2Caps%2C116&sr=8-1-spons&sp_csd=d2lkZ2V0TmFtZT1zcF9hdGY&th=1"
    driver = init_driver()

    try:
        # Step 1: Scrape reviews
        review_data = scrape_reviews(driver, product_url)

        # Step 2: Scrape reviewer profiles
        reviewer_profiles = scrape_reviewer_profiles(driver, review_data)

        # Step 3: Analyze bias and calculate adjusted average score

        #adjusted_average_score = analyze_bias(review_data, reviewer_profiles)

        #print(f"Adjusted Average Score: {adjusted_average_score}")

    finally:
        # Close the browser window
        driver.quit()

if __name__ == "__main__":
    main()