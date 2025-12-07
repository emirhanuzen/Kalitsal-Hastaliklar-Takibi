<>
  <meta charSet="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Kalıtsal Hastalık Takip Sistemi - Giriş</title>
  <link
    href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css"
    rel="stylesheet"
  />
  <link
    rel="stylesheet"
    href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.0/font/bootstrap-icons.css"
  />
  <style
    dangerouslySetInnerHTML={{
      __html:
        "\n        body {\n            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);\n            min-height: 100vh;\n            padding: 20px;\n            display: flex;\n            align-items: center;\n            justify-content: center;\n            margin: 0;\n        }\n        .container {\n            width: 100%;\n            max-width: 1200px;\n            margin: 0 auto;\n        }\n        .login-card {\n            background: white;\n            border-radius: 15px;\n            box-shadow: 0 10px 30px rgba(0,0,0,0.2);\n            padding: 40px;\n            max-width: 450px;\n            width: 100%;\n            margin: 0 auto;\n        }\n        .login-header {\n            text-align: center;\n            margin-bottom: 30px;\n        }\n        .login-header h1 {\n            color: #667eea;\n            font-weight: 700;\n            margin-bottom: 10px;\n        }\n        .form-label {\n            font-weight: 600;\n            color: #333;\n            margin-bottom: 8px;\n        }\n        .form-control:focus {\n            border-color: #667eea;\n            box-shadow: 0 0 0 0.2rem rgba(102, 126, 234, 0.25);\n        }\n        .btn-primary {\n            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);\n            border: none;\n            padding: 12px;\n            font-weight: 600;\n            width: 100%;\n            transition: transform 0.2s;\n        }\n        .btn-primary:hover {\n            transform: translateY(-2px);\n            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);\n        }\n        .btn-register {\n            background: transparent;\n            border: 2px solid #667eea;\n            color: #667eea;\n            padding: 12px;\n            font-weight: 600;\n            width: 100%;\n            margin-top: 10px;\n            transition: all 0.2s;\n        }\n        .btn-register:hover {\n            background: #667eea;\n            color: white;\n        }\n        .alert {\n            border-radius: 10px;\n            border: none;\n        }\n        .divider {\n            text-align: center;\n            margin: 25px 0;\n            position: relative;\n        }\n        .divider::before {\n            content: '';\n            position: absolute;\n            left: 0;\n            top: 50%;\n            width: 100%;\n            height: 1px;\n            background: #e0e0e0;\n        }\n        .divider span {\n            background: white;\n            padding: 0 15px;\n            position: relative;\n            color: #999;\n        }\n    "
    }}
  />
  <div className="container">
    <div className="login-card">
      <div className="login-header">
        <h1>
          <i className="bi bi-heart-pulse-fill" /> Kalıtsal Hastalık Takip
          Sistemi
        </h1>
        <p className="text-muted">Hesabınıza giriş yapın</p>
      </div>
      {"{"}% if message %{"}"}
      <div
        className="alert alert-{{ message_type }} alert-dismissible fade show"
        role="alert"
      >
        <i className="bi bi-{{ 'check-circle' if message_type == 'success' else 'exclamation-triangle' }}-fill" />
        {"{"}
        {"{"} message {"}"}
        {"}"}
        <button type="button" className="btn-close" data-bs-dismiss="alert" />
      </div>
      {"{"}% endif %{"}"}
      <form method="POST" action="/giris" id="loginForm">
        <div className="mb-3">
          <label htmlFor="kurgusal_tc" className="form-label">
            <i className="bi bi-credit-card" /> Kurgusal TC Kimlik No
          </label>
          <input
            type="text"
            className="form-control"
            id="kurgusal_tc"
            name="kurgusal_tc"
            required
            pattern="[0-9]{11}"
            maxLength={11}
            placeholder="11 haneli TC kimlik numaranız"
            defaultValue="{{ request.form.kurgusal_tc if request.form }}"
          />
          <small className="form-text text-muted">
            11 haneli kurgusal TC kimlik numaranızı girin
          </small>
        </div>
        <div className="mb-3">
          <label htmlFor="password" className="form-label">
            <i className="bi bi-lock-fill" /> Şifre
          </label>
          <input
            type="password"
            className="form-control"
            id="password"
            name="password"
            required
            placeholder="Şifrenizi girin"
          />
        </div>
        <button type="submit" className="btn btn-primary">
          <i className="bi bi-box-arrow-in-right" /> Giriş Yap
        </button>
      </form>
      <div className="divider">
        <span>veya</span>
      </div>
      <a href="/kayit-ol" className="btn btn-register">
        <i className="bi bi-person-plus-fill" /> Kayıt Ol
      </a>
    </div>
  </div>
</>
