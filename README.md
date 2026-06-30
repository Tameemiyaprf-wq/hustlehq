# HustleHQ

HustleHQ is a personal side-hustle finance tracker built with Streamlit.

## Features

- Track income from side hustles
- Track expenses and business costs
- Calculate true profit
- Track missing evidence and receipts
- Review profit by side hustle
- Generate weekly review insights
- Export CSV report packs
- Generate PDF reports
- Download backup files
- Use local password protection

## Current version

Phase 1 MVP: personal local finance tracker.

## Important note

This app helps organise records. It does not file anything to HMRC and it is not tax advice.

## Run locally

Install requirements by running:

py -m pip install -r requirements.txt

Run the app with:

py -m streamlit run app.py

## Private data

The app stores personal data locally inside the data folder.

The data folder is ignored by Git so private income records, expense records, goals and password settings are not uploaded.
