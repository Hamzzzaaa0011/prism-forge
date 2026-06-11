def test_robots_txt_points_to_sitemap(client):
    response = client.get("/robots.txt")

    assert response.status_code == 200
    assert response.mimetype == "text/plain"
    assert b"User-agent: *" in response.data
    assert b"Sitemap:" in response.data


def test_sitemap_xml_lists_public_pages(client):
    response = client.get("/sitemap.xml")

    assert response.status_code == 200
    assert response.mimetype == "application/xml"
    assert b"<urlset" in response.data
    assert b"/auth/register" in response.data


def test_static_assets_are_versioned(client):
    response = client.get("/")

    assert response.status_code == 200
    assert b"/static/css/base.css?v=" in response.data
    assert b"/static/js/core/app.js?v=" in response.data
