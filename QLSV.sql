-- Câu 1. Tạo cơ sở dữ liệu và bảng
-- Tạo CSDL quản lý bán hàng đơn giản gồm 3 bảng:
-- Bảng customers
CREATE TABLE customers(
  customer_id INTEGER PRIMARY KEY,
  customer_name text,
  phone text,
  city text);
-- Bảng products
CREATE TABLE products(
  product_id INTEGER PRIMARY KEY,
  product_name text,
  price REAL);
-- Bảng oders
CREATE TABLE orders(
  order_id INTEGER PRIMARY KEY,
  customer_id INTEGER,
  product_id INTEGER,
  order_date text,
  quantity INTEGER,
  FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
  FOREIGN KEY (product_id) REFERENCES products(product_id));

-- Câu 2. Thêm dữ liệu (INSERT)
--Thêm dữ liệu vào bảng Customers
INSERT into customers values (1, 'Nguyễn Tiến Dũng', '0357267596', 'Hưng Yên');
INSERT into customers values (2, 'Nguyễn Chí Thanh', '0354267596', 'Thái Bình');
INSERT into customers values (3, 'Lê Thùy Linh', '0354263423', 'Hà Nội');
--Thêm dữ liệu vào bảng Products
INSERT into products values(1, 'laptop', 20250000);
INSERT into products values(2, 'smartphone', 10350000);
INSERT into products values(3, 'wireless mouse', 32.000);
INSERT INTO Products VALUES (4, 'Keyboard', 50);
--Thêm dữ liệu vào bảng orders
INSERT INTO Orders VALUES (1, 1, 1, '2025-01-10',1);
INSERT INTO Orders VALUES (2, 1, 2, '2025-01-10',2);
INSERT INTO Orders VALUES (3, 2, 3, '2025-01-10',1);
INSERT INTO Orders VALUES (4, 3, 4, '2025-01-15',1);

--3. Bài tập truy vấn cơ bản (SELECT)
--Câu 1
--Hiển thị tất cả thông tin khách hàng.
SELECT * FROM Customers;
--Câu 2
--Hiển thị tên và giá sản phẩm.
SELECT Product_Name, Price FROM Products;
--Câu 3
--Hiển thị các sản phẩm có giá lớn hơn 100.
SELECT * FROM Products
WHERE Price > 100;
--Câu 4
--Hiển thị các khách hàng ở Hà Nội.
SELECT * FROM Customers
WHERE City = 'Hà Nội';


--Câu 5: Hiển thị danh sách sản phẩm sắp xếp theo giá tăng dần.
SELECT * FROM Products
ORDER BY Price ASC;

--Câu 6
--Hiển thị sản phẩm theo giá giảm dần.
SELECT * FROM Products
ORDER BY Price DESC;


--Câu 7: Hiển thị thông tin đơn hàng kèm tên khách hàng.
--cách 1 dùng JOIN
 SELECT * from orders JOIN customers on orders.customer_id=customers.customer_id
--tinh chỉnh
 SELECT orders.order_id, customers.customer_name, orders.order_date from orders 
 JOIN customers on orders.customer_id=customers.customer_id
--cách 2 dùng WHERE 
 SELECT * from orders,customers WHERE orders.customer_id=customers.customer_id
--tinh chỉnh
 SELECT orders.order_id, customers.customer_name, orders.order_date from orders 
 ,customers where orders.customer_id=customers.customer_id
 
/*Câu 8: Hiển thị đơn hàng gồm:
tên khách hàng
tên sản phẩm
số lượng*/
SELECT customers.customer_name,products.product_name,orders.quantity from orders 
JOIN customers on orders.customer_id=customers.customer_id
join products on orders.product_id=products.product_id

--Câu 9: Tính tổng số lượng sản phẩm đã bán.
SELECT SUM(Quantity) AS TongSL FROM Orders;

--Câu 10: Tính giá trung bình của sản phẩm.
SELECT AVG(Price) AS GiaTB FROM Products;

--Câu 11: Đếm số lượng khách hàng.
SELECT COUNT(*) AS SLKH FROM Customers;

--Câu 12: Tính tổng số lượng sản phẩm mỗi khách hàng đã mua.
SELECT SUM(Quantity), customer_id FROM orders GROUP by customer_id

--Câu 13: Cập nhật giá sản phẩm Mouse thành 25.
UPDATE Products SET Price = 25
WHERE Product_Name = 'wireless mouse';

/*Câu 15: Hiển thị
tên khách hàng
tên sản phẩm
số lượng
tổng tiền*/

11. Bài tập tự làm 
1.Thêm 2 khách hàng mới. 
  INSERT into customers values (4, 'Lê Tiến Dũng', '0965302976', 'Hưng Yên');
  INSERT into customers values (5, 'Phùng Thị Ánh', '0967324975', 'Hải Phòng');
2.Thêm 3 sản phẩm mới.
  INSERT into products values(5, 'keyboard', 300000);
  INSERT into products values(6, 'Battery', 320000);
  INSERT INTO Products VALUES (7, 'Charger', 99000);
3.Hiển thị sản phẩm có giá từ 50 đến 500. 
  SELECT * from products where price>=50 and price<=500;
4.Hiển thị 3 sản phẩm đắt nhất.
SELECT * FROM products
ORDER BY price DESC
LIMIT 3;
5.Tính tổng doanh thu bán hàng.
SELECT SUM(products.price * orders.quantity) AS DoanhThu FROM orders
JOIN products ON orders.product_id = products.product_id;
6.Tìm khách hàng mua nhiều sản phẩm nhất.
SELECT customers.customer_name, SUM(orders.quantity) AS TongMua FROM orders
JOIN customers ON orders.customer_id = customers.customer_id
GROUP BY customers.customer_id
ORDER BY TongMua DESC LIMIT 1;
7.Hiển thị đơn hàng mới nhất.
SELECT * FROM orders
ORDER BY order_date DESC LIMIT 1;

12. Bài tập tự làm bổ sung (GROUP BY và các câu lệnh SELECT lồng nhau:
1. Đếm số đơn hàng của mỗi khách hàng
SELECT customer_id, count(*) AS Sodon FROM orders
GROUP by customer_id;

2. Tính tổng số lượng sản phẩm mỗi khách hàng đã mua
SELECT customer_id, SUM(quantity) AS TongSL FROM orders
group by customer_id

3. Tính tổng tiền mỗi khách hàng đã chi
SELECT customers.customer_name, sum(products.price * orders.quantity) AS Tongtien
FROM orders join customers on customers.customer_id = orders.customer_id
JOIN products on orders.product_id=products.product_id
GROUP by customers.customer_id;

4. Hiển thị mỗi sản phẩm đã được bán bao nhiêu lần
SELECT product_id, count(*) AS Lanban from orders
group by product_id;

5. Tìm giá cao nhất, thấp nhất và trung bình của sản phẩm
SELECT MAX(price), MIN(price), AVG(price)
FROM products;

6. Chỉ hiển thị khách hàng mua tổng số lượng > 2
SELECT customer_id, sum(quantity) from orders
GROUP by customer_id
having sum(quantity)>2;

7. Hiển thị các sản phẩm có tổng số lượng bán ra > 1
SELECT product_id,sum(quantity) from orders 
GROUP by product_id
HAVING sum(quantity)>1;

8. Tìm khách hàng chi tiêu nhiều nhất
SELECT customers.customer_name, sum(products.price * orders.quantity) AS Tongtien from orders
join customers on customers.customer_id = orders.customer_id
JOIN products on orders.product_id=products.product_id
group by customers.customer_id
having sum(products.price * orders.quantity) = (SELECT max (Tongtien) from
(SELECT SUM(p.price * o.quantity) AS Tongtien
        FROM orders o
        JOIN products p ON o.product_id = p.product_id
        GROUP BY o.customer_id)
);

9. Tìm ngày có nhiều đơn hàng nhất
SELECT order_date, COUNT(*)
FROM orders
GROUP BY order_date
HAVING COUNT(*) = ( SELECT MAX(SoDon)FROM (
        SELECT COUNT(*) AS SoDon
        FROM orders
        GROUP BY order_date));

10. Hiển thị mỗi khách hàng đã mua bao nhiêu loại sản phẩm khác nhau
SELECT customer_id, count(distinct product_id)
from orders GROUP by customer_id;

11. Tìm sản phẩm có giá cao hơn giá trung bình
SELECT * from products where price > (SELECT avg(price) from products);

12. Tìm khách hàng có số đơn hàng nhiều hơn trung bình
SELECT customer_id, count(*) from orders 
GROUP by customer_id
having count(*)>(select avg(Sodon) from(
SELECT count(*) AS Sodon from orders GROUP by customer_id));


13. Hiển thị sản phẩm có giá cao nhất
SELECT * from products WHERE price = 
(SELECT max(price) from products);

14. Tìm khách hàng đã mua sản phẩm có giá > 100
SELECT DISTINCT c.customer_name from orders o
join customers c on o.customer_id=c.customer_id
join products p on p.product_id=o.product_id
where p.price>100;

15. Hiển thị đơn hàng có số lượng lớn nhất
NÂNG CAO: (KẾT HỢP GROUP BY)
SELECT * from orders where quantity =
(SELECT max(quantity) from orders);

16. Tìm khách hàng có tổng tiền mua hàng lớn hơn trung bình của tất cả khách hàng
SELECT c.customer_name, sum(p.price * o.quantity) AS Tongtien FROM orders o
JOIN customers c on c.customer_id = o.customer_id
join products p on p.product_id = o.product_id
GROUP by c.customer_id
having sum(p.price*o.quantity)>(SELECT avg(Tongtien) from(select SUM(p.price * o.quantity) AS TongTien
        FROM orders o
        JOIN products p ON o.product_id = p.product_id
        GROUP BY o.customer_id));

17. Hiển thị sản phẩm bán chạy nhất (tổng số lượng cao nhất)
SELECT product_id, sum(quantity)AS TongSP 
FROM orders
GROUP by product_id
having TongSP = (SELECT max(TongSP) from(SELECT sum(quantity)AS TongSP 
FROM orders
GROUP by product_id));

18. Tìm khách hàng chưa từng mua hàng
👉 Gợi ý: NOT IN
SELECT * from customers WHERE
customer_id not in (SELECT customer_id from orders);

19. Hiển thị sản phẩm chưa từng được đặt hàng
SELECT * from products WHERE
product_id not in ( SELECT product_id from orders);

20. Tìm khách hàng mua nhiều hơn bất kỳ khách hàng nào ở Hà Nội
SELECT c.customer_name, sum(o.quantity) AS Tongsl from orders o 
join customers c on o.customer_id = c.customer_id
GROUP by c.customer_id
having Tongsl > (SELECT MAX(Tongsl) from(SELECT sum(o.quantity) AS Tongsl from orders o 
join customers c on o.customer_id = c.customer_id
WHERE c.city = 'Hà Nội'
GROUP by o.customer_id));

21. Tìm top 2 khách hàng chi tiêu nhiều nhất (không dùng LIMIT)
SELECT c.customer_name, SUM(o.quantity * p.price) AS TongTien
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
JOIN products p ON o.product_id = p.product_id
GROUP BY c.customer_id
HAVING (SELECT COUNT(*) FROM (
        SELECT SUM(o2.quantity * p2.price) AS TongTien
        FROM orders o2
        JOIN products p2 ON o2.product_id = p2.product_id
        GROUP BY o2.customer_id ) t
WHERE t.TongTien > SUM(o.quantity * p.price)) < 2;

22. Hiển thị các đơn hàng có tổng tiền lớn hơn tổng tiền trung bình của tất cả đơn hàng
SELECT o.order_id, sum(quantity*p.price) AS TongtienSP FROM orders o
JOIN customers c on c.customer_id = o.customer_id
join products p on p.product_id = o.product_id
GROUP by o.order_id
having TongtienSP>(SELECT avg(TongtienSP) from(select sum(quantity*p.price) AS TongtienSP
        FROM orders o
        JOIN products p ON o.product_id = p.product_id
        GROUP BY o.order_id));


23. Tìm khách hàng mua tất cả các sản phẩm
👉 dùng NOT EXISTS ( KHÔNG TỒN TẠI )
SELECT * FROM customers c WHERE NOT EXISTS (
    SELECT * from products p
    WHERE NOT EXISTS (
        SELECT *
        FROM orders o
        WHERE o.customer_id = c.customer_id
        AND o.product_id = p.product_id));

24. Tìm sản phẩm được mua bởi nhiều khách hàng nhất
SELECT product_id, COUNT(DISTINCT customer_id) AS SoKH
FROM orders
GROUP BY product_id
HAVING SoKH = (
    SELECT MAX(SoKH)
    FROM (SELECT COUNT(DISTINCT customer_id) AS SoKH
        FROM orders
        GROUP BY product_id));

25. Với mỗi khách hàng, hiển thị đơn hàng có giá trị cao nhất của họ
👉 gợi ý: subquery trong SELECT hoặc WHERE
SELECT * FROM orders o
JOIN products p on o.product_id = p.product_id
WHERE (o.customer_id, o.quantity * p.price) in (
    SELECT o.customer_id, MAX(o.quantity * p.price)
    FROM orders o
    JOIN products p ON o.product_id = p.product_id
    GROUP BY o.customer_id);
