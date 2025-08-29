USE shastho_regulatory;

-- Seed top stats
INSERT INTO regulatory_stats (total_cases, new_cases_today, active_outbreaks, regions_affected, hospitals_reporting, alerts)
VALUES (12784, 238, 7, 14, 142, 5);

-- Seed regions
INSERT INTO regions (name) VALUES
 ('Dhaka Division'), ('Chittagong Division'), ('Khulna Division'), ('Rajshahi Division'),
 ('Barisal Division'), ('Sylhet Division'), ('Rangpur Division'), ('Mymensingh Division')
ON DUPLICATE KEY UPDATE name = VALUES(name);

-- Seed diseases
INSERT INTO diseases (name, cases, trend, risk_level) VALUES
 ('Dengue Fever', 4582, 'increasing', 'high'),
 ('Cholera', 1237, 'stable', 'medium'),
 ('Tuberculosis', 3456, 'decreasing', 'medium'),
 ('Malaria', 876, 'increasing', 'high'),
 ('Typhoid', 1324, 'stable', 'low'),
 ('Hepatitis A', 645, 'decreasing', 'low'),
 ('COVID-19', 542, 'increasing', 'medium'),
 ('Influenza', 2897, 'increasing', 'medium')
ON DUPLICATE KEY UPDATE cases = VALUES(cases), trend = VALUES(trend), risk_level = VALUES(risk_level);

-- Seed outbreaks
INSERT INTO outbreaks (disease, region, cases, status, trend, start_date, severity) VALUES
 ('Dengue Fever', 'Dhaka Division', 278, 'Active', 'Increasing', '2023-07-01', 'High'),
 ('Cholera', 'Barisal Division', 156, 'Active', 'Stable', '2023-06-15', 'Medium'),
 ('Malaria', 'Chittagong Division', 124, 'Active', 'Increasing', '2023-06-25', 'High'),
 ('COVID-19', 'Dhaka Division', 87, 'Active', 'Increasing', '2023-07-10', 'Medium'),
 ('Influenza', 'Sylhet Division', 203, 'Active', 'Decreasing', '2023-06-10', 'Medium');

-- Seed region summaries
INSERT INTO region_summary (region, total_cases, active_outbreaks, population_affected, hospital_capacity) VALUES
 ('Dhaka Division', 4125, 3, '0.82%', '76%'),
 ('Chittagong Division', 2784, 2, '0.54%', '65%'),
 ('Khulna Division', 1653, 1, '0.48%', '52%'),
 ('Rajshahi Division', 945, 0, '0.31%', '40%'),
 ('Barisal Division', 1241, 1, '0.58%', '59%');

-- Seed primary diseases per region
INSERT INTO region_primary_diseases (region, disease) VALUES
 ('Dhaka Division', 'Dengue Fever'),('Dhaka Division', 'COVID-19'),('Dhaka Division', 'Tuberculosis'),
 ('Chittagong Division', 'Malaria'),('Chittagong Division', 'Typhoid'),('Chittagong Division', 'Dengue Fever'),
 ('Khulna Division', 'Cholera'),('Khulna Division', 'Typhoid'),
 ('Rajshahi Division', 'Tuberculosis'),('Rajshahi Division', 'Influenza'),
 ('Barisal Division', 'Cholera'),('Barisal Division', 'Hepatitis A');

-- Seed monthly trends (Jan..Jul = 1..7)
-- Dengue
INSERT INTO monthly_trends (disease, month_index, cases) VALUES
 ('Dengue', 1, 125),('Dengue', 2, 156),('Dengue', 3, 243),('Dengue', 4, 375),('Dengue', 5, 456),('Dengue', 6, 678),('Dengue', 7, 892);
-- Malaria
INSERT INTO monthly_trends (disease, month_index, cases) VALUES
 ('Malaria', 1, 223),('Malaria', 2, 198),('Malaria', 3, 210),('Malaria', 4, 227),('Malaria', 5, 252),('Malaria', 6, 286),('Malaria', 7, 312);
-- Cholera
INSERT INTO monthly_trends (disease, month_index, cases) VALUES
 ('Cholera', 1, 342),('Cholera', 2, 287),('Cholera', 3, 265),('Cholera', 4, 301),('Cholera', 5, 285),('Cholera', 6, 312),('Cholera', 7, 345);
-- COVID-19
INSERT INTO monthly_trends (disease, month_index, cases) VALUES
 ('COVID-19', 1, 556),('COVID-19', 2, 423),('COVID-19', 3, 378),('COVID-19', 4, 402),('COVID-19', 5, 435),('COVID-19', 6, 489),('COVID-19', 7, 542);
-- Influenza
INSERT INTO monthly_trends (disease, month_index, cases) VALUES
 ('Influenza', 1, 675),('Influenza', 2, 789),('Influenza', 3, 856),('Influenza', 4, 945),('Influenza', 5, 1023),('Influenza', 6, 1287),('Influenza', 7, 1543);


