INSERT INTO public."book" (title, author, translator, description, pdf_loc, cover_img_loc, published_on, genre) VALUES
('Moby Dick; Or, The Whale','Herman Melville','','A tale of the whale hunt and revenge.','/static/pdfs/Moby Dick; Or, The Whale.pdf','/static/images/Moby Dick; Or, The Whale.png','1851-10-18','Fiction'),
('Pride and Prejudice','Jane Austen','','A classic romance novel.','/static/pdfs/Pride and Prejudice.pdf','/static/images/Pride and Prejudice.png','1813-01-28','Romance'),
('Romeo and Juliet','William Shakespeare','','A timeless tragedy of star-crossed lovers.','/static/pdfs/Romeo and Juliet.pdf','/static/images/Romeo and Juliet.png','1597-01-01','Drama');

INSERT INTO public."user" (username, email, password, phone, gender, address, is_admin) VALUES
('Jane_Doe', 'Jane_Doe@admin.com', 'abcd1234','1234567890','Female','Pune',True),
('John_Doe', 'John_Doe@admin.com', 'abcd1234','1234567890','Male','Pune',True),
('Naman_Gupta', 'Naman_Gupta@admin.com', 'abcd1234','1234567890','Male','Pune',True);