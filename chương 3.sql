CREATE TABLE KHOA (
     makhoa TEXT(10) NOT NULL,
	 tenkhoa TEXT(50),
	 PRIMARY KEY ('makhoa')
);
INSERT INTO KHOA values ('heh', 'Kinh Tế số')
-- thêm cột tên sv vào bảng KHOA
alter table KHOA add tensv text(20);
alter table KHOA add ghichu text (30);
-- xóa cột ghi chú
alter table KHOA drop ghichu;
-- thêm dữ liệu vào cột
insert into khoa values ('ối dồi ôi', 'kinh tế hé', 'Độc Lạ Bình Dương');
-- xóa bản ghi
DELETE from khoa where makhoa="heh"
-- sửa gtri 1 hàng
update khoa set tenkhoa="Khoa Kinh Tế Số"
where makhoa="ối dồi ôi"
-- Tạo thêm bảng
create table QLSV (
   masv text (20) not null,
   tensv text(15),
   PRIMARY KEY ('masv')
   );
  -- xem các bản ghi của KHOA
select * from Khoa;
select tenkhoa from khoa;
select * from Khoa where makhoa="heh";
select * from Khoa where makhoa="ối dồi ôi";


