# KVSH-Prototype
Real time credit card recommendation engine built with Python, Flask, HTML and JavaScript

# KVSH Payment Decision Engine

A real time rule-based system that recommends the best credit card 
at checkout to maximise cashback and rewards.

## What it does
- Compares 10 Indian credit cards across 6 spend categories
- Applies merchant-specific rates (Amazon, Swiggy, Flipkart, Zomato etc.)
- Tracks monthly reward caps and partial cap logic
- Handles edge cases: min transaction, fuel surcharge waiver, acceptance risk
- Returns a confident recommendation in under 2 seconds

## Stack
Python · Flask · JavaScript · REST API

## Run it
pip install flask
python app.py
Open http://localhost:8080

## Live demo
[Click here](https://4a8eac44-4dbc-4067-97cf-aa8ebed8cb6d-00-2dwtz85yfohh6.pike.replit.dev/)
