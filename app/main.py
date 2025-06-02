# app/main.py

from datetime import datetime, timedelta
import os

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt

from app.routers.recurso import router as dados_router
from app.routers.healthz import router as health_router  

# ─── Configurações de JWT ──────────────────────────────────────────────────────
SECRET_KEY = os.environ.get("API_SECRET_KEY") # em produção, guarde fora do código!
if not SECRET_KEY:
    raise ValueError("API_SECRET_KEY não definida no ambiente")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD")
# ────────────────────────────────────────────────────────────────────────────────

app = FastAPI(
    title="API Vinicultura Embrapa",
    version="1.1.0",
    description="Dados de vitivinicultura com health-check e autenticação JWT"
)

# ─── Rota de login / token ─────────────────────────────────────────────────────
@app.post("/token", summary="Gera token de acesso")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    # Exemplo simples “admin” / “password”
    if not (form_data.username == ADMIN_USERNAME and form_data.password == ADMIN_PASSWORD):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"sub": form_data.username, "exp": expire}
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return {"access_token": token, "token_type": "bearer"}
# ────────────────────────────────────────────────────────────────────────────────


def verify_token(token: str = Depends(oauth2_scheme)):
    """
    Dependência que valida o token JWT em cada requisição protegida.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token inválido ou expirado",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        return username
    except JWTError:
        raise credentials_exception


# ─── 1) Health-check PÚBLICO (NÃO exige token) ─────────────────────────────────
app.include_router(
    health_router,
    prefix="/healthz",
    tags=["monitoramento"]
)
# Agora, chamar GET http://127.0.0.1:8000/healthz/ retorna status=ok e detalhe, sem pedir token.


# ─── 2) Endpoints de dados (protegidos por JWT) ─────────────────────────────────
app.include_router(
    dados_router,
    dependencies=[Depends(verify_token)],
    responses={401: {"description": "Não autorizado"}},
    tags=["dados"]
)
# Qualquer rota definida em `dados_router` estará disponível só com "Authorization: Bearer <JWT>".

# ─── 3) Rota raiz (também pública) ───────────────────────────────────────────────
@app.get("/", tags=["raiz"], summary="Rota raiz")
async def read_root():
    return {"message": "API vinicultura está rodando!"}
