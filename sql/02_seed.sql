USE dalal_street_pro;

INSERT INTO stocks (ticker,company,exchange,sector,industry,market_cap_cat,current_price,prev_close,day_high,day_low,week_52_high,week_52_low,volume,pe_ratio,pb_ratio,dividend_yield,face_value,market_cap,is_fo_enabled) VALUES
('RELIANCE','Reliance Industries Ltd','NSE','Energy','Oil & Gas','LARGE_CAP',2850.00,2801.80,2868.00,2796.00,3024.00,2180.00,4820000,28.4,2.1,0.35,10,1930000000000,TRUE),
('TCS','Tata Consultancy Services','NSE','IT','Software','LARGE_CAP',3920.00,3883.00,3954.00,3871.00,4254.00,3311.00,1240000,32.1,13.8,1.42,1,1420000000000,TRUE),
('HDFCBANK','HDFC Bank Ltd','NSE','Banking','Private Bank','LARGE_CAP',1680.00,1687.00,1698.00,1664.00,1880.00,1363.00,6320000,18.6,2.9,1.21,1,1270000000000,TRUE),
('INFY','Infosys Ltd','NSE','IT','Software','LARGE_CAP',1940.00,1921.00,1958.00,1915.00,1953.00,1351.00,3140000,26.4,7.2,2.35,5,810000000000,TRUE),
('ICICIBANK','ICICI Bank Ltd','NSE','Banking','Private Bank','LARGE_CAP',1120.00,1108.00,1134.00,1101.00,1196.00,895.00,8240000,19.2,3.1,0.89,2,790000000000,TRUE),
('HINDUNILVR','Hindustan Unilever Ltd','NSE','FMCG','Consumer Goods','LARGE_CAP',2480.00,2461.00,2498.00,2452.00,2767.00,2172.00,980000,58.3,11.4,1.68,1,582000000000,TRUE),
('BAJFINANCE','Bajaj Finance Ltd','NSE','Finance','NBFC','LARGE_CAP',7240.00,7189.00,7312.00,7168.00,8192.00,6187.00,680000,31.2,6.8,0.41,2,436000000000,TRUE),
('TATAMOTORS','Tata Motors Ltd','NSE','Automobile','Auto OEM','LARGE_CAP',780.00,804.00,812.00,774.00,1068.00,601.00,11200000,9.8,2.4,0.51,2,286000000000,TRUE),
('WIPRO','Wipro Ltd','NSE','IT','Software','LARGE_CAP',490.00,484.00,496.00,481.00,572.00,384.00,4200000,22.1,4.1,0.20,2,268000000000,TRUE),
('ADANIENT','Adani Enterprises Ltd','NSE','Conglomerate','Diversified','LARGE_CAP',2940.00,2794.00,3012.00,2780.00,3743.00,1430.00,2100000,62.3,8.4,0.04,1,334000000000,TRUE),
('SUNPHARMA','Sun Pharmaceutical','NSE','Pharma','Pharmaceuticals','LARGE_CAP',1620.00,1598.00,1638.00,1591.00,1762.00,1023.00,1480000,38.4,5.2,0.74,1,388000000000,FALSE),
('LTIM','LTIMindtree Ltd','NSE','IT','Software','LARGE_CAP',5840.00,5792.00,5912.00,5768.00,6796.00,4312.00,420000,28.9,8.1,0.86,1,172000000000,FALSE),
('SUZLON','Suzlon Energy Ltd','NSE','Energy','Wind Energy','MID_CAP',58.40,53.88,64.20,52.10,76.00,18.00,84200000,41.2,8.9,0.00,2,79000000000,FALSE),
('IRFC','Indian Railway Finance Corp','NSE','Finance','Govt Finance','MID_CAP',192.40,183.50,201.80,181.20,229.00,87.00,24800000,30.8,4.1,1.04,10,252000000000,FALSE),
('ZOMATO','Zomato Ltd','NSE','Tech','Food Delivery','MID_CAP',178.60,185.60,182.40,174.20,229.00,114.00,32400000,312.0,7.8,0.00,1,158000000000,FALSE),
('PAYTM','One97 Communications','NSE','Tech','Fintech','MID_CAP',428.00,456.00,441.00,421.00,998.00,310.00,8400000,0.00,3.2,0.00,1,27000000000,FALSE),
('NYKAA','FSN E-Commerce','NSE','Tech','E-Commerce','MID_CAP',172.00,165.00,178.00,163.00,235.00,119.00,4800000,198.0,9.4,0.00,1,49000000000,FALSE),
('COALINDIA','Coal India Ltd','NSE','Energy','Mining','LARGE_CAP',468.00,477.00,472.00,461.00,544.00,311.00,6200000,8.4,3.1,6.21,10,288000000000,TRUE),
('ONGC','Oil & Natural Gas Corp','NSE','Energy','Oil & Gas','LARGE_CAP',268.00,274.00,271.00,264.00,346.00,178.00,14200000,7.2,1.1,4.28,5,337000000000,TRUE),
('YESBANK','Yes Bank Ltd','NSE','Banking','Private Bank','SMALL_CAP',24.80,23.60,26.10,23.20,32.85,15.00,84000000,42.0,1.8,0.00,2,78000000000,FALSE);

INSERT INTO mutual_funds (scheme_code,fund_name,fund_house,category,sub_category,current_nav,prev_nav,aum_cr,expense_ratio,rating,returns_1y,returns_3y,returns_5y) VALUES
('INF109K01VQ1','Axis Bluechip Fund - Direct Growth','Axis Mutual Fund','EQUITY','Large Cap',68.42,67.98,32840.00,0.450,5,18.4,14.2,16.8),
('INF204K01U42','Mirae Asset Large Cap Fund - Direct','Mirae Asset','EQUITY','Large Cap',102.18,101.54,38920.00,0.540,5,19.2,15.1,17.4),
('INF174K01LS2','Parag Parikh Flexi Cap - Direct','PPFAS','EQUITY','Flexi Cap',74.82,74.21,54210.00,0.590,5,28.1,20.4,24.8),
('INF200K01RB8','SBI Small Cap Fund - Direct','SBI Mutual Fund','EQUITY','Small Cap',148.64,147.21,24180.00,0.680,4,42.8,24.1,28.6),
('INF179K01BB8','HDFC Nifty 50 Index Fund - Direct','HDFC Mutual Fund','INDEX','Nifty 50',184.21,183.42,12480.00,0.100,4,18.8,13.9,16.2),
('INF277K01ZL8','Aditya Birla SL ELSS Tax Relief 96','Aditya Birla','ELSS','Tax Saving',48.92,48.54,14820.00,0.890,3,16.2,12.8,15.4),
('INF090I01239','Franklin India Prima Fund - Direct','Franklin Templeton','EQUITY','Mid Cap',2184.30,2171.80,12840.00,0.850,4,32.4,18.6,22.1),
('INF194K01C48','Kotak Liquid Fund - Direct','Kotak','LIQUID','Liquid',4284.18,4283.14,42180.00,0.200,5,7.1,6.8,6.9);

INSERT INTO users (username,email,phone,pan_number,password_hash,balance,risk_profile) VALUES
('arjun_kapoor','arjun@dalal.com','9876543210','ABCPK1234D','$2b$12$dummyhasharjun000000000000000000000000000000',1000000.00,'AGGRESSIVE'),
('priya_sharma','priya@dalal.com','9876543211','XYZPS5678F','$2b$12$dummyhashpriya000000000000000000000000000000',1500000.00,'MODERATE'),
('rahul_mehta','rahul@dalal.com','9876543212','LMNRM9012G','$2b$12$dummyhashrahul000000000000000000000000000000',750000.00,'CONSERVATIVE');

INSERT INTO portfolios (user_id,name,description,color,is_default) VALUES
(1,'Core Holdings','Blue chip long term portfolio','#6366f1',TRUE),
(1,'Growth Bets','Mid & small cap aggressive picks','#10b981',FALSE),
(2,'Wealth Builder','Balanced diversified portfolio','#f59e0b',TRUE),
(3,'Retirement Fund','Safe conservative picks','#3b82f6',TRUE);

INSERT INTO holdings (portfolio_id,stock_id,quantity,avg_buy_price) VALUES
(1,1,50,2650.00),(1,2,20,3600.00),(1,3,100,1580.00),(1,4,80,1820.00),
(2,13,5000,32.00),(2,14,500,148.00),(2,17,200,120.00),
(3,5,100,1050.00),(3,6,50,2380.00),(3,11,80,1420.00),
(4,18,300,420.00),(4,19,400,240.00);

INSERT INTO trades (portfolio_id,stock_id,trade_type,product_type,quantity,price,brokerage,stt) VALUES
(1,1,'BUY','CNC',50,2650.00,20.00,132.50),(1,2,'BUY','CNC',20,3600.00,20.00,72.00),
(1,3,'BUY','CNC',100,1580.00,20.00,158.00),(2,13,'BUY','CNC',5000,32.00,20.00,160.00),
(2,13,'BUY','CNC',2000,28.00,20.00,56.00),(3,5,'BUY','CNC',100,1050.00,20.00,105.00),
(4,18,'BUY','CNC',300,420.00,20.00,126.00);

INSERT INTO sip_plans (portfolio_id,stock_id,amount,frequency,start_date,next_due,total_invested,units_purchased,installments_done) VALUES
(1,2,10000,'MONTHLY','2024-01-15','2025-06-15',50000.00,13.42,5),
(1,1,5000,'MONTHLY','2024-03-01','2025-06-01',25000.00,9.48,5),
(3,5,8000,'MONTHLY','2024-02-10','2025-06-10',40000.00,38.10,5);

INSERT INTO mf_holdings (portfolio_id,fund_id,units,avg_nav,invested_amount) VALUES
(1,1,1460.12,68.49,100000.00),(1,3,1337.79,74.75,100000.00),
(3,5,2714.92,184.18,500000.00),(3,6,2042.84,48.95,100000.00);

INSERT INTO dividends (stock_id,amount_per_share,dividend_type,ex_date,record_date,pay_date) VALUES
(1,9.00,'FINAL','2025-07-12','2025-07-13','2025-07-28'),
(2,28.00,'FINAL','2025-07-08','2025-07-09','2025-07-24'),
(3,19.50,'FINAL','2025-06-28','2025-06-30','2025-07-15'),
(4,21.00,'INTERIM','2025-10-25','2025-10-26','2025-11-10'),
(18,25.50,'FINAL','2025-08-02','2025-08-04','2025-08-20');

INSERT INTO ipos (company_name,ticker,price_band_low,price_band_high,lot_size,issue_size_cr,open_date,close_date,listing_date,listing_price,gmp,subscription_times,status) VALUES
('Ola Electric Mobility','OLAELEC',72,76,195,6145.60,'2024-08-02','2024-08-06','2024-08-09',75.99,22.00,4.27,'LISTED'),
('Bajaj Housing Finance','BAJAJHFL',66,70,214,6560.00,'2024-09-09','2024-09-11','2024-09-16',150.00,62.00,64.21,'LISTED'),
('Swiggy','SWIGGY',371,390,38,11327.43,'2024-11-06','2024-11-08','2024-11-13',412.00,14.00,3.59,'LISTED'),
('Hexaware Technologies','HEXAWARE',674,708,21,8750.00,'2025-02-12','2025-02-14','2025-02-19',745.00,48.00,2.66,'LISTED'),
('Ather Energy','ATHER',304,321,46,2981.00,'2025-04-28','2025-04-30','2025-05-06',297.00,-15.00,1.40,'LISTED'),
('New India Solar Ltd','NISOLAR',180,200,75,1200.00,'2025-06-10','2025-06-12','2025-06-19',NULL,35.00,0.00,'UPCOMING'),
('GreenTech Infra Ltd','GRNTECH',240,260,57,800.00,'2025-06-18','2025-06-20','2025-06-27',NULL,18.00,0.00,'UPCOMING');

INSERT INTO benchmarks (name,value,change_pct,recorded_at) VALUES
('NIFTY50',22450.30,0.82,'2025-05-20'),('SENSEX',73960.80,0.73,'2025-05-20'),
('NIFTY_BANK',48120.60,-0.47,'2025-05-20'),('NIFTY_IT',36840.00,1.15,'2025-05-20'),
('NIFTY_MIDCAP',48210.40,1.34,'2025-05-20');

INSERT INTO market_news (headline,source,stock_id,category) VALUES
('Reliance Jio to launch 5G in 100 new cities, analyst target revised to Rs 3200','Economic Times',1,'COMPANY'),
('TCS wins $300M deal from European banking giant, stock at 52-week high','Moneycontrol',2,'COMPANY'),
('RBI holds repo rate at 6.5 percent, markets rally on banking stocks','Mint',NULL,'MACRO'),
('Suzlon Energy wins 500MW wind order from NTPC, stock jumps 8 percent','BSE Filing',13,'COMPANY'),
('FIIs net buyers for 5th straight session, Rs 4200 Cr inflow into India','CNBCTV18',NULL,'FII'),
('SEBI tightens F&O rules, weekly expiry limited to one index per exchange','LiveMint',NULL,'REGULATION'),
('Infosys Q4 revenue up 8.6 percent YoY, raises FY26 growth guidance','ET Markets',4,'EARNINGS');

INSERT INTO watchlist (user_id,stock_id,notes) VALUES
(1,7,'Watch for Q3 results'),(1,12,'Strong IT mid-cap pick'),(1,15,'High risk monitoring'),
(2,8,'Waiting for dip below Rs 750'),(2,10,'Adani recovery play'),(3,11,'Pharma defensive pick');
