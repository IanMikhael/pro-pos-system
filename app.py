import streamlit as st
import mysql.connector
import pandas as pd
import urllib.parse
from PIL import Image # LIBRARY UNTUK OLAH GAMBAR
import io              # LIBRARY UNTUK BYTE STREAM

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Pro-POS System", layout="wide", page_icon="🛍️")

# --- SESSION STATE ---
if 'cart' not in st.session_state:
    st.session_state.cart = []
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'user_role' not in st.session_state:
    st.session_state['user_role'] = None

# --- CUSTOM CSS (DIPERBARUI AGAR SERAGAM & RESPONSIVE) ---
st.markdown("""
    <style>
    .stApp { background-color: #f4f7f6; }
    [data-testid="stSidebar"] { background-color: #1e293b; color: white; }
    
    .product-card {
        background-color: white;
        border-radius: 10px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        border: 1px solid #e2e8f0;
        margin-bottom: 25px;
        position: relative;
        overflow: hidden;
        display: flex;
        flex-direction: column;
        height: 100%;
        
        background-color: #ffffff;
        border: 1px solid #f0f2f6;
        border-radius: 15px;
        padding: 0px;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        margin-bottom: 20px;
        overflow: hidden;
    }

    [data-testid="stImage"] img {
        width: 100%;
        aspect-ratio: 1 / 1;
        object-fit: cover;
        border-radius: 15px 15px 0 0;
    }

    .badge-discount {
        position: absolute;
        top: 10px;
        left: 10px;
        background-color: #ef4444;
        color: white;
        padding: 3px 10px;
        border-radius: 5px;
        font-weight: bold;
        font-size: 0.8em;
        z-index: 10;
    }

    .card-content { 
        padding: 1px 1px; 
        text-align: center; 
        flex-grow: 1;
    }

    .card-title { 
        font-size: 1.1em; 
        font-weight: bold; 
        color: #1e293b; 
        min-height: 30px; 
        display: -webkit-box;
        -webkit-line-clamp: 2;
        -webkit-box-orient: vertical;
        overflow: hidden;
    }

    .price-old { color: #94a3b8; text-decoration: line-through; font-size: 0.85em; margin-bottom: -5px; }
    .card-price { color: #2563eb; font-size: 1.4em; font-weight: 800; margin: 5px 0; }
    
    /* ✨ Elegan & Mewah — Luxury UI/UX untuk Login */
.login-container {
    background: linear-gradient(145deg, #fafafa, #f5f7fa);
    padding: 50px 40px;
    border-radius: 24px;
    box-shadow: 
        0 12px 30px rgba(0, 0, 0, 0.06),
        0 4px 6px rgba(0, 0, 0, 0.03),
        inset 0 1px 0 rgba(255, 255, 255, 0.8);
    border: 1px solid rgba(226, 232, 240, 0.6);
    margin-top: 50px;
    position: relative;
    overflow: hidden;
}

/* ✨ Subtle gold accent (opsional: bisa disesuaikan dengan branding TackaGud) */
.login-container::before {
    content: "";
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 4px;
    background: linear-gradient(90deg, #d4af37, #f9d423, #d4af37); /* Emas halus */
    border-radius: 2px 2px 0 0;
}

.login-header {
    text-align: center;
    margin-bottom: 36px;
}

.login-header h1 {
    color: #1e293b;
    font-family: 'Georgia', 'Times New Roman', serif; /* Elegan & timeless */
    font-size: 28px;
    font-weight: 700;
    letter-spacing: -0.5px;
    margin-bottom: 10px;
    position: relative;
}

/* ✨ Tiny cross or dove icon — opsional untuk nuansa rohani */
.login-header h1::after {
    content: "✝";
    font-size: 18px;
    color: #a16207;
    opacity: 0.6;
    margin-left: 6px;
}

.login-header p {
    color: #64748b;
    font-size: 15px;
    line-height: 1.5;
    max-width: 80%;
    margin: 0 auto;
    font-family: 'Segoe UI', system-ui, sans-serif;
}

/* ✨ Form Streamlit styling — refined */
div[data-testid="stForm"] {
    border: none !important;
    padding: 0 !important;
    background: transparent !important;
}

.login-box {
    background: white;
    padding: 48px 40px;
    border-radius: 24px;
    box-shadow: 
        0 15px 40px rgba(0, 0, 0, 0.05),
        0 5px 15px rgba(0, 0, 0, 0.02);
    border: 1px solid rgba(226, 232, 240, 0.7);
    text-align: center;
    transition: transform 0.3s ease;
}

.login-box:hover {
    transform: translateY(-3px);
}

/* ✨ Input & button: lebih halus, mewah, interaktif */
.stTextInput > div {
    background: #fdfdfd !important;
    border: 1px solid #e2e8f0 !important;
    border-radius: 14px !important;
    padding: 2px !important;
    transition: all 0.25s ease;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.02) !important;
}

.stTextInput input {
    border-radius: 12px !important;
    padding: 14px 18px !important;
    font-size: 16px !important;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    color: #1e293b !important;
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
}

.stTextInput input:focus {
    outline: none !important;
    box-shadow: 0 0 0 3px rgba(212, 175, 55, 0.2) !important; /* Soft gold glow */
}

/* ✨ Tombol Login: tombol utama mewah */
.stButton button {
    background: linear-gradient(135deg, #1e293b, #334155) !important;
    color: white !important;
    font-weight: 600 !important;
    font-size: 16px !important;
    border-radius: 14px !important;
    padding: 14px 28px !important;
    width: 100% !important;
    border: none !important;
    box-shadow: 
        0 4px 12px rgba(30, 41, 59, 0.2),
        0 2px 4px rgba(30, 41, 59, 0.1) !important;
    transition: all 0.3s ease !important;
    letter-spacing: 0.5px;
}

.stButton button:hover {
    background: linear-gradient(135deg, #334155, #475569) !important;
    transform: translateY(-2px);
    box-shadow: 
        0 6px 16px rgba(30, 41, 59, 0.25),
        0 4px 8px rgba(30, 41, 59, 0.15) !important;
}

.stButton button:active {
    transform: translateY(0);
}

/* ✨ Micro-interaction: subtle glow on focus/active */
.stTextInput input::placeholder {
    color: #94a3b8 !important;
    opacity: 1;
}

/* Floating Shopping Cart Button */
    .floating-cart {
        position: fixed;
        bottom: 30px;
        right: 30px;
        background: linear-gradient(135deg, #2563eb, #1e40af);
        color: white;
        width: 65px;
        height: 65px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 10px 25px rgba(37, 99, 235, 0.4);
        cursor: pointer;
        z-index: 1000;
        transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        border: 2px solid white;
    }

    .floating-cart:hover {
        transform: scale(1.1) rotate(-10deg);
    }

    /* Badge Jumlah Item di Atas Icon */
    .cart-count {
        position: absolute;
        top: -5px;
        right: -5px;
        background: #ef4444;
        color: white;
        font-size: 12px;
        font-weight: bold;
        width: 24px;
        height: 24px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        border: 2px solid white;
    }         
    </style>
    """, unsafe_allow_html=True)

# --- FUNGSI PROSES GAMBAR ---
def process_image(uploaded_file):
    if uploaded_file is not None:
        img = Image.open(uploaded_file)
        if img.mode in ("RGBA", "P"):
            background = Image.new("RGB", img.size, (255, 255, 255))
            background.paste(img, mask=img.split()[3] if img.mode == "RGBA" else None)
            img = background
        else:
            img = img.convert("RGB")
        width, height = img.size
        min_dim = min(width, height)
        left = (width - min_dim) / 2
        top = (height - min_dim) / 2
        right = (width + min_dim) / 2
        bottom = (height + min_dim) / 2
        img = img.crop((left, top, right, bottom))
        img = img.resize((400, 400), Image.LANCZOS)
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=90)
        return buf.getvalue()
    return None

# --- KONEKSI DATABASE ---
# def get_connection():
#     return mysql.connector.connect(
#         host="localhost", user="root", password="", database="pos_system"
#     )

# def get_connection():
#     return mysql.connector.connect(
#         host="gateway01.ap-southeast-1.prod.aws.tidbcloud.com",
#         port=4000,
#         user="2i4trFqj4YhT8Uo.root",
#         password="366deYjPy9LOrl64",
#         database="test",
#         autocommit=True
#     )

def get_connection():
    return mysql.connector.connect(
        host=st.secrets["mysql"]["host"],
        port=st.secrets["mysql"]["port"],
        user=st.secrets["mysql"]["user"],
        password=st.secrets["mysql"]["password"],
        database=st.secrets["mysql"]["database"],
        autocommit=True
    )

def run_query(query, params=None):
    try:
        with get_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                cursor.execute(query, params or ())
                if query.strip().upper().startswith("SELECT"):
                    return cursor.fetchall()
                conn.commit()
                return None
    except Exception as e:
        st.error(f"Database Error: {e}")
        return None

# --- FUNGSI SETTINGS WA ---
def get_wa_number():
    res = run_query("SELECT wa_number FROM settings WHERE id = 1")
    return res[0]['wa_number'] if res else "628123456789"



def login_admin(username, password):
    user = run_query("SELECT * FROM admins WHERE username = %s AND password = %s", (username, password))
    return user[0] if user else None

def main():
    st.sidebar.markdown("<h1 style='text-align: center; color: white;'>🏪 Pro-POS</h1>", unsafe_allow_html=True)
    st.sidebar.markdown("---")
    
    if st.session_state['logged_in']:
        # Navigasi berdasarkan Role
        nav_options = ["📦 Kelola Produk", "🏷️ Kategori & Brand"]
        if st.session_state['user_role'] == 'admin':
            nav_options.append("👤 Kelola Admin")
            nav_options.append("⚙️ Pengaturan WA")
        nav_options.extend(["🏠 Katalog User", "🚪 Logout"])
        menu = st.sidebar.selectbox("Navigasi Admin", nav_options)
    else:
        menu = st.sidebar.selectbox("Navigasi User", ["🏠 Katalog Produk", "🔐 Login Admin"])

    # --- 1. HALAMAN KATALOG CUSTOMER ---
    if menu in ["🏠 Katalog Produk", "🏠 Katalog User"]:
        st.markdown("<h1 style='text-align: center;'>🛍️ Katalog Produk</h1>", unsafe_allow_html=True)
        col_katalog, col_keranjang = st.columns([3, 1])

        with col_katalog:
            # Filter baris (Kategori, Brand, Search)
            c_cat, c_brand, c_search = st.columns([1, 1, 2])
            
            cats_data = run_query("SELECT * FROM categories")
            cat_list = ["Semua Kategori"] + [c['category_name'] for c in (cats_data if cats_data else [])]
            
            brands_data = run_query("SELECT * FROM brands")
            brand_list = ["Semua Brand"] + [b['brand_name'] for b in (brands_data if brands_data else [])]
            
            with c_cat: filter_cat = st.selectbox("Kategori:", cat_list)
            with c_brand: filter_brand = st.selectbox("Brand:", brand_list)
            with c_search: search_term = st.text_input("Cari Produk...", placeholder="Ketik nama produk...")

            query_show = """
                SELECT p.*, c.category_name, b.brand_name 
                FROM products p
                JOIN categories c ON p.category_id = c.id
                JOIN brands b ON p.brand_id = b.id
                WHERE p.name LIKE %s
            """
            params = [f"%{search_term}%"]
            if filter_cat != "Semua Kategori":
                query_show += " AND c.category_name = %s"
                params.append(filter_cat)
            if filter_brand != "Semua Brand":
                query_show += " AND b.brand_name = %s"
                params.append(filter_brand)
                
            produk = run_query(query_show, tuple(params))
            if produk:
                cols = st.columns(3)
                for i, item in enumerate(produk):
                    with cols[i % 3]:
                        st.markdown('<div class="product-card">', unsafe_allow_html=True)
                        if item.get('discount_pct', 0) > 0:
                            st.markdown(f'<div class="badge-discount">-{item["discount_pct"]}%</div>', unsafe_allow_html=True)
                        
                        img = item['image'] if item.get('image') else "https://via.placeholder.com/500x500?text=No+Image"
                        st.image(img, use_container_width=True)
                        
                        st.markdown(f"""<div class="card-content">
                            <div style="color:gray; font-size:0.8em;">{item['brand_name']} | {item['category_name']}</div>
                            <div class="card-title">{item['name']}</div>""", unsafe_allow_html=True)
                        
                        if item.get('discount_pct', 0) > 0:
                            st.markdown(f'<div class="price-old">Rp {item["original_price"]:,}</div>', unsafe_allow_html=True)
                        st.markdown(f"""<div class="card-price">Rp {item['price']:,}</div></div>""", unsafe_allow_html=True)
                        
                        if st.button(f"🛒 Tambah", key=f"btn_{item['id']}", use_container_width=True):
                            found = False
                            for cart_item in st.session_state.cart:
                                if cart_item['nama'] == item['name']:
                                    cart_item['qty'] += 1
                                    found = True
                                    break
                            if not found:
                                st.session_state.cart.append({"nama": item['name'], "harga": item['price'], "qty": 1})
                            st.toast(f"Ditambahkan: {item['name']}")
                            st.rerun()
                        st.markdown('</div>', unsafe_allow_html=True)
            else: st.info("Produk tidak ditemukan.")

        with col_keranjang:
            st.markdown("### 🛒 Keranjang Saya")
            if not st.session_state.cart:
                st.write("Keranjang masih kosong.")
            else:
                subtotal = 0
                for i, item_cart in enumerate(st.session_state.cart):
                    subtotal += item_cart['harga'] * item_cart['qty']
                    c_del, c_txt = st.columns([1, 4])
                    if c_del.button("❌", key=f"del_{i}"):
                        st.session_state.cart.pop(i); st.rerun()
                    c_txt.markdown(f"**{item_cart['nama']}**\n<small>{item_cart['qty']} x Rp {item_cart['harga']:,}</small>", unsafe_allow_html=True)
                
                st.markdown("---")
                st.subheader(f"Total: Rp {subtotal:,}")
                nama_pembeli = st.text_input("Nama Anda", placeholder="Contoh: Budi")
                
                # if st.button("✅ Bayar via WhatsApp", use_container_width=True, type="primary"):
                #     if not nama_pembeli:
                #         st.error("Masukkan nama dulu min!")
                #     else:
                #         wa_target = get_wa_number()
                #         list_belanja = "\n".join([f"{j+1}. {it['nama']} ({it['qty']}x) - Rp {it['harga']*it['qty']:,}" for j, it in enumerate(st.session_state.cart)])
                #         text_wa = f"*ORDER BARU - PRO-POS*\n\nNama: {nama_pembeli}\n---------------------------\n{list_belanja}\n---------------------------\n*Subtotal: Rp {subtotal:,}*"
                #         st.markdown(f'<meta http-equiv="refresh" content="0;URL=\'https://wa.me/{wa_target}?text={urllib.parse.quote(text_wa)}\'" />', unsafe_allow_html=True)
                
                # if st.button("Bersihkan Keranjang", use_container_width=True):
                #     st.session_state.cart = []; st.rerun()

                if st.button("✅ Bayar via WhatsApp", use_container_width=True, type="primary"):
                    if not nama_pembeli:
                        st.error("Masukkan nama dulu min!")
                    else:
                        # 1. Ambil nomor WA terbaru dari database (Hasil input Admin)
                        wa_target = get_wa_number()
                        
                        # 2. Susun pesan belanjaan
                        list_belanja = "\n".join([f"{j+1}. {it['nama']} ({it['qty']}x) - Rp {it['harga']*it['qty']:,}" for j, it in enumerate(st.session_state.cart)])
                        text_wa = f"*ORDER BARU - PRO-POS*\n\nNama: {nama_pembeli}\n---------------------------\n{list_belanja}\n---------------------------\n*Subtotal: Rp {subtotal:,}*"
                        
                        # 3. Buat URL resmi WhatsApp API
                        wa_url = f"https://api.whatsapp.com/send?phone={wa_target}&text={urllib.parse.quote(text_wa)}"
                        
                        # 4. SOLUSI: Gunakan JavaScript untuk memaksa buka di TAB BARU (Bukan Refresh)
                        # Ini cara paling ampuh di Streamlit Cloud agar tidak diblokir browser
                        js = f"window.open('{wa_url}')"
                        st.components.v1.html(f"""
                            <script>{js}</script>
                            <div style="text-align:center; padding:10px; background:#e1ffc7; border-radius:10px;">
                                <p>Menghubungkan ke WhatsApp...</p>
                                <a href="{wa_url}" target="_blank" style="color:#25d366; font-weight:bold;">Klik di sini jika tidak otomatis terbuka</a>
                            </div>
                        """, height=100)

#login admin
    elif menu == "🔐 Login Admin":
        _, col_login, _ = st.columns([1, 1.5, 1])
        
        with col_login:
            # Gunakan container pembungkus agar semua masuk dalam satu frame
            with st.container(border=True): # Menggunakan parameter border asli Streamlit untuk keamanan layout
                st.markdown("""
                    <div style="text-align: center; margin-bottom: 20px;">
                        <img src="https://cdn-icons-png.flaticon.com/512/6024/6024190.png" width="80">
                        <h2 style="margin-top:10px;">Welcome Back</h2>
                        <p style="color: gray; font-size: 0.9em;">Silakan login untuk mengelola toko Anda</p>
                    </div>
                """, unsafe_allow_html=True)
                
                with st.form("login_admin_form", clear_on_submit=False):
                    u = st.text_input("Username", placeholder="Masukkan username...")
                    p = st.text_input("Password", type="password", placeholder="Masukkan password...")
                    
                    st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
                    submit = st.form_submit_button("🚀 Gass Login...", use_container_width=True)
                    
                    if submit:
                        user = login_admin(u, p)
                        if user: 
                            st.session_state['logged_in'] = True
                            st.session_state['user_role'] = user.get('role', 'subadmin')
                            st.success(f"Login Berhasil!")
                            st.balloons()
                            st.rerun()
                        else: 
                            st.error("Username atau Password salah!")

            st.markdown("<p style='text-align:center; color:#94a3b8; font-size:0.8em; margin-top:15px;'>Pro-POS System v2.0 • Secure Login</p>", unsafe_allow_html=True)

# --- 3. KELOLA PRODUK (GRID 4 KOLOM WEB, 2 KOLOM MOBILE & BUTTON KIRI-KANAN) ---
    elif menu == "📦 Kelola Produk":
        st.title("📦 Management Produk")

        # CSS untuk memaksa grid 4 kolom di Web dan tetap 2 kolom di Mobile
        st.markdown("""
            <style>
            /* Pengaturan baris agar flexibel */
            div[data-testid="stHorizontalBlock"] {
                display: flex !important;
                flex-wrap: wrap !important;
                flex-direction: row !important;
                gap: 0px !important;
            }

            /* Desktop: 4 Produk per baris (Lebar ~24%) */
            div[data-testid="stHorizontalBlock"] > div {
                flex: 1 1 24% !important;
                min-width: 24% !important;
                padding: 10px !important;
            }

            /* Mobile: 2 Produk per baris (Lebar ~48%) */
            @media (max-width: 640px) {
                div[data-testid="stHorizontalBlock"] > div {
                    flex: 1 1 48% !important;
                    min-width: 48% !important;
                    padding: 5px !important;
                }
            }

            .manage-card {
                background: white;
                border-radius: 12px;
                padding: 10px;
                margin-bottom: 15px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.05);
                border: 1px solid #e2e8f0;
                display: flex;
                flex-direction: column;
                height: 100%;
            }

            [data-testid="stImage"] img {
                border-radius: 8px;
                aspect-ratio: 1 / 1;
                object-fit: cover;
            }
            </style>
        """, unsafe_allow_html=True)

        # Fungsi Popup Edit (Dialog)
        @st.dialog("📝 Edit Produk")
        def edit_popup(product_id):
            res_edit = run_query("SELECT * FROM products WHERE id = %s", (product_id,))
            if res_edit:
                item = res_edit[0]
                with st.form("edit_form_popup", clear_on_submit=True):
                    enama = st.text_input("Nama Produk", value=item['name'])
                    ce1, ce2 = st.columns(2)
                    
                    cat_ids = list(cat_opt.values())
                    brand_ids = list(brand_opt.values())
                    c_idx = cat_ids.index(item['category_id']) if item['category_id'] in cat_ids else 0
                    b_idx = brand_ids.index(item['brand_id']) if item['brand_id'] in brand_ids else 0

                    esel_cat = ce1.selectbox("Kategori", list(cat_opt.keys()), index=c_idx)
                    esel_brand = ce2.selectbox("Brand", list(brand_opt.keys()), index=b_idx)
                    
                    eprice_base = ce1.number_input("Harga Dasar", value=int(item.get('original_price', item['price'])))
                    ediskon_pct = ce2.number_input("Diskon (%)", 0, 100, value=int(item.get('discount_pct', 0)))
                    estock = st.number_input("Stok", value=item['stock'])
                    efoto = st.file_uploader("Ganti Foto (Kosongkan jika tetap)", type=['jpg', 'png', 'jpeg'])

                    if st.form_submit_button("✅ Simpan Perubahan", use_container_width=True):
                        efinal = int(eprice_base - (ediskon_pct/100 * eprice_base))
                        img_up = process_image(efoto) if efoto else item['image']
                        run_query("UPDATE products SET name=%s, category_id=%s, brand_id=%s, original_price=%s, discount_pct=%s, price=%s, stock=%s, image=%s WHERE id=%s", 
                                  (enama, cat_opt[esel_cat], brand_opt[esel_brand], eprice_base, ediskon_pct, efinal, estock, img_up, product_id))
                        st.success("Data berhasil diupdate!")
                        st.rerun()

        # Load Options
        cats = run_query("SELECT * FROM categories")
        cat_opt = {c['category_name']: c['id'] for c in (cats if cats else [])}
        brands = run_query("SELECT * FROM brands")
        brand_opt = {b['brand_name']: b['id'] for b in (brands if brands else [])}

        # Form Tambah Produk
        with st.expander("➕ Tambah Produk Baru"):
            with st.form("add_product", clear_on_submit=True):
                col1, col2 = st.columns(2)
                nama = col1.text_input("Nama Produk")
                sel_cat = col2.selectbox("Kategori", list(cat_opt.keys()))
                sel_brand = col1.selectbox("Brand", list(brand_opt.keys()))
                c_harga, c_diskon = st.columns(2)
                h_input = c_harga.number_input("Harga Normal", min_value=0)
                p_diskon = c_diskon.number_input("Diskon (%)", 0, 100)
                stok = st.number_input("Stok", min_value=0)
                foto = st.file_uploader("Upload Foto", type=['jpg', 'png', 'jpeg'])
                
                if st.form_submit_button("Simpan Produk", use_container_width=True):
                    h_final = int(h_input - ((p_diskon/100)*h_input))
                    img_bytes = process_image(foto)
                    run_query("INSERT INTO products (name, category_id, brand_id, original_price, discount_pct, price, stock, image) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", 
                              (nama, cat_opt[sel_cat], brand_opt[sel_brand], h_input, p_diskon, h_final, stok, img_bytes))
                    st.success("Produk disimpan!"); st.rerun()

        st.divider()
        search_query = st.text_input("🔍 Cari Inventori...", placeholder="Nama, Brand, Kategori...")
        data_inv = run_query("""SELECT p.*, c.category_name, b.brand_name FROM products p 
                                JOIN categories c ON p.category_id = c.id 
                                JOIN brands b ON p.brand_id = b.id
                                WHERE p.name LIKE %s OR c.category_name LIKE %s OR b.brand_name LIKE %s
                                ORDER BY p.id DESC""", (f"%{search_query}%", f"%{search_query}%", f"%{search_query}%"))

        if data_inv:
            # ✨ n_cols = 4 untuk tampilan Desktop
            n_cols = 4 
            for i in range(0, len(data_inv), n_cols):
                cols = st.columns(n_cols)
                for j in range(n_cols):
                    if i + j < len(data_inv):
                        p = data_inv[i + j]
                        with cols[j]:
                            st.markdown('<div class="manage-card">', unsafe_allow_html=True)
                            
                            # Foto Produk
                            if p.get('image'):
                                st.image(p['image'], use_container_width=True)
                            else:
                                st.markdown('<div style="height:100px; background:#f1f5f9; display:flex; align-items:center; justify-content:center; border-radius:8px;">🖼️</div>', unsafe_allow_html=True)
                            
                            # Info Produk Ringkas
                            st.markdown(f"""
                                <div style="text-align:center; margin-top:8px; flex-grow:1; margin-bottom:10px;">
                                    <div style="font-weight:bold; font-size:12px; line-height:1.2; height:30px; overflow:hidden;">{p['name']}</div>
                                    <div style="color:#2563eb; font-weight:bold; font-size:13px; margin:4px 0;">Rp {p['price']:,}</div>
                                    <div style="font-size:10px; color:#64748b;">Stok: {p['stock']}</div>
                                </div>
                            """, unsafe_allow_html=True)
                            
                            # --- TOMBOL AKSI KIRI KANAN ---
                            btn_col1, btn_col2 = st.columns([3, 2])
                            
                            if btn_col1.button("📝", key=f"ed_{p['id']}", use_container_width=True):
                                edit_popup(p['id'])
                            
                            if btn_col2.button("🗑️", key=f"del_{p['id']}", use_container_width=True):
                                run_query("DELETE FROM products WHERE id = %s", (p['id'],))
                                st.rerun()
                                
                            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("Inventori tidak ditemukan.")

    # --- 4. KATEGORI & BRAND (FIXED: FULL HORIZONTAL MOBILE) ---
    elif menu == "🏷️ Kategori & Brand":
        st.markdown("<h2 style='text-align: center;'>🏷️ Management Kategori & Brand</h2>", unsafe_allow_html=True)
        
        # CSS sakti untuk memaksa tata letak tetap horizontal di HP
        st.markdown("""
            <style>
            /* Container utama untuk setiap baris kategori/brand */
            .inline-management-row {
                display: flex !important;
                flex-direction: row !important;
                align-items: center !important;
                justify-content: space-between !important;
                padding: 10px 5px;
                border-bottom: 1px solid #eee;
                background: white;
            }
            /* Bagian teks (ID dan Nama) */
            .item-left {
                display: flex;
                align-items: center;
                gap: 10px;
                flex: 1;
                min-width: 0;
            }
            .item-id { color: #94a3b8; font-size: 12px; font-family: monospace; }
            .item-name { 
                font-weight: 600; 
                color: #1e293b; 
                white-space: nowrap; 
                overflow: hidden; 
                text-overflow: ellipsis;
            }
            /* Bagian tombol aksi agar tetap di kanan */
            .item-right {
                display: flex;
                gap: 5px;
                margin-left: 10px;
            }
            /* Perkecil tombol agar muat dalam satu baris di HP */
            div.stButton > button {
                padding: 2px 8px !important;
                height: auto !important;
                min-height: 32px !important;
                margin: 0 !important;
            }
            </style>
        """, unsafe_allow_html=True)

        tab1, tab2 = st.tabs(["📁 Daftar Kategori", "🏢 Daftar Brand"])

        with tab1:
            with st.expander("➕ Tambah Kategori Baru"):
                with st.form("form_cat", clear_on_submit=True):
                    new_c = st.text_input("Nama Kategori Baru")
                    if st.form_submit_button("Simpan Kategori", use_container_width=True):
                        if new_c: run_query("INSERT INTO categories (category_name) VALUES (%s)", (new_c,)); st.rerun()
            
            cat_data = run_query("SELECT * FROM categories ORDER BY id DESC")
            if cat_data:
                for c in cat_data:
                    # CEK MODE EDIT
                    if st.session_state.get("edit_cat_id") == c['id']:
                        with st.form(f"edit_cat_{c['id']}"):
                            nc = st.text_input("Edit Nama", value=c['category_name'])
                            c1, c2 = st.columns(2)
                            if c1.form_submit_button("✅ Update", use_container_width=True):
                                run_query("UPDATE categories SET category_name=%s WHERE id=%s", (nc, c['id']))
                                del st.session_state["edit_cat_id"]; st.rerun()
                            if c2.form_submit_button("Batal", use_container_width=True):
                                del st.session_state["edit_cat_id"]; st.rerun()
                    else:
                        # TAMPILAN VIEW: ID | NAMA (KIRI) dan TOMBOL (KANAN)
                        # Kita gunakan st.columns dengan rasio yang tidak akan stack otomatis
                        col_info, col_actions = st.columns([4, 2])
                        
                        with col_info:
                            st.markdown(f"""
                                <div style="display: flex; align-items: center; gap: 10px; height: 35px;">
                                    <span style="color: #94a3b8; font-size: 12px;">#{c['id']}</span>
                                    <span style="font-weight: 600; font-size: 14px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{c['category_name']}</span>
                                </div>
                            """, unsafe_allow_html=True)
                        
                        with col_actions:
                            # Gunakan kolom lagi di dalam untuk menaruh tombol berdampingan
                            act1, act2 = st.columns(2)
                            if act1.button("📝", key=f"ec_{c['id']}", use_container_width=True):
                                st.session_state["edit_cat_id"] = c['id']; st.rerun()
                            if act2.button("🗑️", key=f"dc_{c['id']}", use_container_width=True):
                                run_query("DELETE FROM categories WHERE id=%s", (c['id'],)); st.rerun()
                        
                        st.markdown("<hr style='margin: 2px 0; opacity: 0.1;'>", unsafe_allow_html=True)

        with tab2:
            with st.expander("➕ Tambah Brand Baru"):
                with st.form("form_brand", clear_on_submit=True):
                    new_b = st.text_input("Nama Brand Baru")
                    if st.form_submit_button("Simpan Brand", use_container_width=True):
                        if new_b: run_query("INSERT INTO brands (brand_name) VALUES (%s)", (new_b,)); st.rerun()
            
            brand_data = run_query("SELECT * FROM brands ORDER BY id DESC")
            if brand_data:
                for b in brand_data:
                    if st.session_state.get("edit_brand_id") == b['id']:
                        with st.form(f"edit_brand_{b['id']}"):
                            nb = st.text_input("Edit Nama", value=b['brand_name'])
                            b1, b2 = st.columns(2)
                            if b1.form_submit_button("✅ Update", use_container_width=True):
                                run_query("UPDATE brands SET brand_name=%s WHERE id=%s", (nb, b['id']))
                                del st.session_state["edit_brand_id"]; st.rerun()
                            if b2.form_submit_button("Batal", use_container_width=True):
                                del st.session_state["edit_brand_id"]; st.rerun()
                    else:
                        col_info, col_actions = st.columns([4, 2])
                        
                        with col_info:
                            st.markdown(f"""
                                <div style="display: flex; align-items: center; gap: 10px; height: 35px;">
                                    <span style="color: #94a3b8; font-size: 12px;">#{b['id']}</span>
                                    <span style="font-weight: 600; font-size: 14px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{b['brand_name']}</span>
                                </div>
                            """, unsafe_allow_html=True)
                        
                        with col_actions:
                            act1, act2 = st.columns(2)
                            if act1.button("📝", key=f"eb_{b['id']}", use_container_width=True):
                                st.session_state["edit_brand_id"] = b['id']; st.rerun()
                            if act2.button("🗑️", key=f"db_{b['id']}", use_container_width=True):
                                run_query("DELETE FROM brands WHERE id=%s", (b['id'],)); st.rerun()
                        
                        st.markdown("<hr style='margin: 2px 0; opacity: 0.1;'>", unsafe_allow_html=True)

    # --- 5. KELOLA ADMIN ---
    elif menu == "👤 Kelola Admin":
        if st.session_state.get('user_role') != 'admin':
            st.error("Akses Ditolak!"); st.stop()
        st.title("👤 Manajemen Akun")
        with st.expander("➕ Tambah Akun Baru"):
            with st.form("form_add_admin", clear_on_submit=True):
                new_u = st.text_input("Username Baru"); new_p = st.text_input("Password Baru", type="password")
                new_r = st.selectbox("Role", ["admin", "subadmin"])
                if st.form_submit_button("Daftarkan Admin"):
                    if new_u and new_p:
                        run_query("INSERT INTO admins (username, password, role) VALUES (%s, %s, %s)", (new_u, new_p, new_r))
                        st.success("Akun berhasil dibuat!"); st.rerun()
        st.divider(); st.subheader("Daftar Akun")
        admins_list = run_query("SELECT * FROM admins")
        if admins_list:
            for adm in admins_list:
                c1, c2, c3 = st.columns([1, 4, 2])
                c1.write(f"#{adm['id']}")
                if st.session_state.get("edit_admin_id") == adm['id']:
                    with c2:
                        eu = st.text_input("Username", value=adm['username'], key=f"u_{adm['id']}")
                        ep = st.text_input("Password Baru", value=adm['password'], type="password", key=f"p_{adm['id']}")
                        er = st.selectbox("Role", ["admin", "subadmin"], index=0 if adm['role']=='admin' else 1, key=f"r_{adm['id']}")
                    with c3:
                        if st.button("✅", key=f"save_adm_{adm['id']}"):
                            run_query("UPDATE admins SET username=%s, password=%s, role=%s WHERE id=%s", (eu, ep, er, adm['id']))
                            del st.session_state["edit_admin_id"]; st.rerun()
                        if st.button("❌", key=f"can_adm_{adm['id']}"): del st.session_state["edit_admin_id"]; st.rerun()
                else:
                    c2.write(f"**{adm['username']}** (`{adm['role']}`)")
                    be, bd = c3.columns(2)
                    if be.button("📝", key=f"ed_adm_{adm['id']}"): st.session_state["edit_admin_id"] = adm['id']; st.rerun()
                    if bd.button("🗑️", key=f"dl_adm_{adm['id']}"): run_query("DELETE FROM admins WHERE id = %s", (adm['id'],)); st.rerun()
                st.markdown("<hr style='margin:0; border-color:#eee;'>", unsafe_allow_html=True)

    # --- 6. PENGATURAN WA ---
    elif menu == "⚙️ Pengaturan WA":
        if st.session_state.get('user_role') != 'admin':
            st.error("Akses Ditolak!"); st.stop()
        st.title("⚙️ Pengaturan Nomor WhatsApp")
        current_wa = get_wa_number()
        with st.form("wa_settings"):
            new_wa = st.text_input("Nomor WhatsApp Tujuan (Gunakan format 62...)", value=current_wa)
            if st.form_submit_button("Simpan Perubahan"):
                run_query("UPDATE settings SET wa_number = %s WHERE id = 1", (new_wa,))
                st.success("Nomor WhatsApp berhasil diperbarui!"); st.rerun()

    elif menu == "🚪 Logout":
        st.session_state.update({'logged_in': False, 'user_role': None}); st.rerun()

if __name__ == "__main__":
    main()