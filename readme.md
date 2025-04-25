# CSV Processing and Invoice Scraping Script

This script reads a source CSV file containing website details and credentials and uses [browser-use](https://github.com/browser-use/browser-use) to following instructions as defined in the source file.

## IMPORTANT

* browser-use is early release, still buggy with known issues
* It is quite slow, they are currently working on cacheing mechanisms to improve performance
* Although the username / password are never sent to the LLM, if they appear on the website / login screen in clear text they will be sent. This also applies to any other information visible on the screen. Use a reputable LLM that does not train on your prompts, or host your own LLM
* There is a known issue when using obfusicated username / password that stops the controller from extracting formatted output, as such it is not currently possible to extract website data AND use obfusication in this release
* The current release is ignoring browser window size directives, so the browser will occupy full screen
* Don't attempt to use the device when browser-use is running, this will cause the window to lose focus and it doesn't behave very well. Just leave it to finish.

## Requirements

* Built and tested with Python 3.13.3, Mac OS Sonoma Version 14.1.1
* Dependencies listed in `requirements.txt`
* Access to the websites specified in the `source.csv`.
* An API key for the OpenAI (specify in .env).

## Setup

1.  **Clone the Repository (if applicable):**
    ```bash
    git clone [your_repository_url]
    cd [your_repository_directory]
    ```

2.  **Install Dependencies:**
    Navigate to the project's root directory in your terminal and run:
    ```bash
    pip install -r requirements.txt
    ```

3.  **API Keys and Environment Variables:**
    Copy .env-example to .env and add you openAI API key.

    The script currently uses OpenAI LLM, consult Browser Use docs to change LLMs and env key.

## Input CSV Format (`./input/source.csv`)

The script expects an input CSV file named `source.csv` inside an `input` directory in the project's root. It must contain a header row.

| Column Name | Required | Type/Description                      | Example                                      |
| :---------- | :------- | :------------------------------------ | :------------------------------------------- |
| `siteName`  | Yes      | String, minimum 1 character.          | `ExampleSite One`                            |
| `siteURL`   | Yes      | Valid HTTPS URL.                      | `https://service.talktalk.co.uk/billsandpayments/latestbill` - It is best to provide the full link to the page containing the info you want e.g. /invoices/downloads, your site will probably redirect to login, then redirect back to this page             |  
| `username`  | Yes      | String, minimum 1 character.          | `user123`                                    |
| `password`  | Yes      | String, minimum 1 character.          | `passABC`                                    |
| `navHelper` | Yes      | String, minimum 1 character. Text describing the operation.                          | `Find the latest paid invoice and downaload the PDF` - This instruction will be added to the hardcoded 'Login with x_name and x_password if required. ' instruction      |

**Example `source.csv`:**

```csv
siteName,siteURL,username,password,navHelper
Test,https://file-examples.com/,test,test,Download the smallest doc file.
Test 2,https://examplefile.com/,test,test,Download the smallest txt file.
```

## Output CSV Format (`./output/[timestamp]/output.csv`)

| Column Name   | Description                                  | Example         |
| :------------ | :------------------------------------------- | :-------------- |
| `siteName`    | The name of the site from the input.         | `ExampleSite One` |
| `siteUrl`     | The site url.     | `https://.....`          |
| `status`      | The status of the processed row.             | `Success OR failure reason`           |


**Example `output_[timestamp].csv` (contents will vary based on processing):**

```csv
siteName,siteURL,status
Test,https://file-examples.com/,Success
Test 2,https://examplefile.com/,Success
```
## File download location (`./output/[timestamp]/[siteName]/`)

Each download will be saved under the timestamped directory, in a new directory named as the site name

## Running the Script

1.  Ensure you have followed the setup steps, including installing dependencies and creating the `.env` file.
2.  Place your `source.csv` file inside the `./input` directory.
3.  Open your terminal, navigate to the project's root directory, and run the script using the Python interpreter:
    ```bash
    python scrape.py
    ```
