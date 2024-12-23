def reply_text(): 
    return "Gambar yang anda kirim pada percakapan ini akan dicek secara otomatis ada atau tidaknya blur. Jika ada gangguan dengan pengecekan anda dapat menghubungi kontak sales atau pemasaran anda."
def reply_unknown(): 
    return "Percakapan ini hanya dapat digunakan untuk mengumpulkan dokumen untuk pengecekan. Mohon hubungi kontak anda untuk informasi lebih lanjut."
def reply_document_blur(blur_pages): 
    return "Dokumen yang anda kirim memiliki blur pada halaman " + str(blur_pages) + ", mohon ambil ulang gambar pada halaman tersebut"
def reply_document_clear(): 
    return "Dokumen yang anda kirim akan kami proses untuk pengecekan"
def reply_image_blur():
    return "Gambar anda kirim memiliki blur, mohon ambil ulang gambar tersebut"
def reply_image_clear():
    return "Gambar dokumen anda kirim akan kami proses untuk pengecekan"



