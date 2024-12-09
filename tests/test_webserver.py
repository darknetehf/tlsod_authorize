class TestWebServer:
    def test_missing_domain(self, session, url):
        response = session.get(url)
        assert response.status_code == 400

    def test_domain_not_found(self, session, url):
        params = {"domain": "notfound.com"}
        response = session.get(url, params=params)
        assert response.status_code == 404

    def test_domain_found(self, session, url):
        params = {"domain": "test.com"}
        response = session.get(url, params=params)
        assert response.status_code == 200

    def test_domain_found_mixed_case(self, session, url):
        params = {"domain": "TesT.Com"}
        response = session.get(url, params=params)
        assert response.status_code == 200
