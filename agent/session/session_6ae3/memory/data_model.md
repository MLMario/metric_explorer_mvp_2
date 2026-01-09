# Data Model Documentation

## Overview
- Total files analyzed: 1
- Target metric found: YES (conversion_rate)
- Data date range: 2024-12-10 to 2024-12-24 (15 days)

## Tables

### sessions_dec_2024.csv
- **Rows**: 360 (plus 1 header row)
- **Columns**: 7

| Column Name | Data Type | Description | Sample Values |
|-------------|-----------|-------------|---------------|
| date | date | Session date in YYYY-MM-DD format | 2024-12-10, 2024-12-24 |
| device_type | string | Platform/device where session occurred | web, ios, android |
| category | string | Product category being browsed | electronics, fashion, home, groceries |
| user_type | string | Whether user is new or returning | new, returning |
| sessions | integer | Total number of user sessions on this date/segment | 273–1778 |
| orders | integer | Total completed orders on this date/segment | 8–121 |
| conversion_rate | decimal | Calculated conversion rate (orders/sessions) | 0.0148–0.0759 |

**Key Dimensions**:
- `device_type` (3 values: web, ios, android) - allows segmentation across platforms
- `category` (4 values: electronics, fashion, home, groceries) - allows category-level analysis
- `user_type` (2 values: new, returning) - allows comparison between new and returning user behavior
- `date` (15 days) - allows temporal analysis across the baseline and anomaly periods

## Data Structure Details

### Date Range
- **Baseline Period**: 2024-12-10 to 2024-12-16 (7 days before checkout change)
- **Anomaly Period**: 2024-12-17 to 2024-12-24 (8 days after checkout change on 2024-12-16)
- This aligns perfectly with the user's context: drop started Dec 17 and persisted through Dec 24

### Data Granularity
- Data is aggregated at the daily level by device_type, category, and user_type combination
- Each row represents metrics for a specific segment on a specific date
- Sessions and orders are counts; conversion_rate is pre-calculated

### Data Completeness
- All 360 rows contain non-null values across all 7 columns
- No missing or corrupted data detected
- Conversion rates are consistently decimal format (4-5 decimal places)
- Sessions and orders are positive integers

## Relationships
- No foreign keys or relationships between tables (single table dataset)
- Data is fully denormalized with all relevant dimensions in one table

## Target Metric
- **Metric**: conversion_rate
- **Found in**: sessions_dec_2024.csv (column: conversion_rate)
- **Calculation**: orders / sessions (pre-calculated in the dataset)
- **Availability**: Available for all date/platform/category/user-type combinations

## Data Quality Assessment

### Strengths
- Target metric is present and directly available
- Complete coverage across all dimensional combinations
- Consistent data types and formats
- No null values or missing data
- Consistent decimal precision for conversion rates

### Insights for Analysis
- Web platform likely dominates traffic (3 device types covered)
- Data spans the critical periods: 7 days before checkout change (Dec 10-16) and 8 days after (Dec 17-24)
- Four product categories provide granular segmentation options
- Both new and returning users are tracked, allowing user cohort analysis
- Sufficient row count (360) allows for statistical analysis across all segments

## Validation Result
✓ **VALIDATION PASSED**: All required data is present and valid. The conversion_rate metric is directly available in the CSV, and supporting columns (sessions, orders, date, device_type, category, user_type) enable comprehensive hypothesis testing across multiple dimensions.
