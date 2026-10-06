/* Navbar compartida según sesión y rol. */
function renderNav() {
  const mount = document.getElementById("nav");
  if (!mount) return;
  const u = currentUser();
  const link = (href, label) => `<a href="${href}" class="px-3 py-2 rounded hover:bg-indigo-500 text-white text-sm">${label}</a>`;
  let links = "";
  if (u) {
    links += link("catalog.html", "Catálogo");
    links += link("cart.html", "Carrito");
    links += link("orders.html", "Pedidos");
    links += link("recommendations.html", "Recomendaciones");
    if (u.role === "Administrador") links += link("admin.html", "Admin");
  } else {
    links += link("login.html", "Login") + link("register.html", "Registro");
  }
  mount.innerHTML = `
    <nav class="bg-indigo-600">
      <div class="max-w-6xl mx-auto px-4 py-3 flex flex-wrap items-center gap-2">
        <a href="catalog.html" class="text-white font-bold mr-4">E-Commerce</a>
        ${links}
        ${u ? `<span class="text-indigo-200 text-sm ml-auto mr-2">${u.role}</span><button onclick="logout()" class="px-3 py-2 rounded bg-indigo-800 text-white text-sm">Salir</button>` : ""}
      </div>
    </nav>`;
}
document.addEventListener("DOMContentLoaded", renderNav);
