from processing.image_preprocessing import preprocess_image
p='uploads/1771486088_test_img.png'
print('Calling preprocess on', p)
res=preprocess_image(p)
print('Result:', res)
