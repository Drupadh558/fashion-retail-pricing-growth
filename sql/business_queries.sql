-- 1. Category & Brand Performance (Category Management KPI)
SELECT 
    brand,
    COUNT(*) AS total_skus,
    ROUND(AVG(selling_price), 2) AS avg_selling_price,
    ROUND(AVG(discount_pct), 1) AS avg_discount_pct,
    ROUND(AVG(rating), 2) AS avg_rating,
    SUM(estimated_revenue_proxy) AS total_revenue_proxy
FROM products
GROUP BY brand
HAVING total_skus >= 20
ORDER BY total_revenue_proxy DESC
LIMIT 15;

-- 2. Discount Elasticity & Margin Protection (Demand Management KPI)
SELECT 
    discount_band,
    COUNT(*) AS sku_count,
    ROUND(AVG(selling_price), 2) AS avg_price,
    ROUND(AVG(rating_count), 1) AS avg_demand_velocity,
    SUM(estimated_revenue_proxy) AS band_revenue_proxy
FROM products
GROUP BY discount_band
ORDER BY avg_demand_velocity DESC;

-- 3. Price Tier Distribution (Assortment & Pricing Strategy)
SELECT 
    price_tier,
    COUNT(*) AS sku_count,
    ROUND(AVG(discount_pct), 1) AS avg_discount,
    ROUND(AVG(rating), 2) AS avg_rating
FROM products
GROUP BY price_tier
ORDER BY sku_count DESC;

-- 4. High-Potential Ad Monetization Targets (Ads & Brand Visibility KPI)
SELECT 
    brand,
    COUNT(*) AS eligible_skus,
    ROUND(AVG(rating), 2) AS avg_rating,
    ROUND(AVG(rating_count), 1) AS avg_visibility_count,
    ROUND(AVG(selling_price), 2) AS avg_price
FROM products
WHERE ad_pitch_target = 'High Potential (Pitch Ads)'
GROUP BY brand
HAVING eligible_skus >= 5
ORDER BY avg_rating DESC, eligible_skus DESC
LIMIT 20;