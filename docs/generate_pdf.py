"""Gera PDF técnico; adicione prints reais em docs/prints e atualize integrantes.txt.
Dependência de documentação: pip install -r docs/requirements.txt
Executar: python3 docs/generate_pdf.py
"""
from pathlib import Path
from xml.sax.saxutils import escape
import textwrap
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Preformatted, Image, KeepTogether
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'docs/HydroGuard-Documentacao-CICD.pdf'
FONT_PATH = Path('/usr/share/fonts/truetype/dejavu')
if FONT_PATH.exists():
    pdfmetrics.registerFont(TTFont('HG', str(FONT_PATH/'DejaVuSans.ttf')))
    pdfmetrics.registerFont(TTFont('HG-Bold', str(FONT_PATH/'DejaVuSans-Bold.ttf')))
    pdfmetrics.registerFont(TTFont('HG-Mono', str(FONT_PATH/'DejaVuSansMono.ttf')))
else:
    pdfmetrics.registerFontFamily('HG', normal='Helvetica', bold='Helvetica-Bold')
    # Built-ins allow rendering on computers without these fonts.
FONT = 'HG' if FONT_PATH.exists() else 'Helvetica'
BOLD = 'HG-Bold' if FONT_PATH.exists() else 'Helvetica-Bold'
MONO = 'HG-Mono' if FONT_PATH.exists() else 'Courier'
NAVY = colors.HexColor('#123344')
TEAL = colors.HexColor('#078879')
LIGHT = colors.HexColor('#EDF5F5')
INK = colors.HexColor('#243746')
AMBER = colors.HexColor('#9A5E05')
styles = {
    'title': ParagraphStyle('title', fontName=BOLD, fontSize=31, leading=36, textColor=NAVY, spaceAfter=18),
    'h1': ParagraphStyle('h1', fontName=BOLD, fontSize=21, leading=26, textColor=NAVY, spaceAfter=16),
    'h2': ParagraphStyle('h2', fontName=BOLD, fontSize=12, leading=17, textColor=TEAL, spaceBefore=13, spaceAfter=7),
    'body': ParagraphStyle('body', fontName=FONT, fontSize=10, leading=15, textColor=INK, spaceAfter=10),
    'small': ParagraphStyle('small', fontName=FONT, fontSize=8, leading=11, textColor=INK, spaceAfter=5),
    'label': ParagraphStyle('label', fontName=BOLD, fontSize=9, leading=14, textColor=TEAL, spaceAfter=10),
    'code': ParagraphStyle('code', fontName=MONO, fontSize=7.5, leading=11, textColor=NAVY, spaceAfter=10),
}
story = []
def para(text, style='body'):
    return Paragraph(escape(text).replace('\n','<br/>'), styles[style])
def add(text, style='body'):
    story.append(para(text,style))
def heading(n,text):
    add('HYDROGUARD  /  DOCUMENTAÇÃO TÉCNICA','label')
    add(f'{n:02d}  {text}','h1')
def table(rows,widths=None):
    data = [[para(str(value),'small') for value in row] for row in rows]
    tab=Table(data, colWidths=widths or [5*cm,12*cm],hAlign='LEFT')
    tab.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,0),LIGHT),('VALIGN',(0,0),(-1,-1),'TOP'),
        ('LINEBELOW',(0,0),(-1,0),1,TEAL),('LINEBELOW',(0,1),(-1,-1),0.4,colors.HexColor('#D6E3E7')),
        ('LEFTPADDING',(0,0),(-1,-1),9),('RIGHTPADDING',(0,0),(-1,-1),9),
        ('TOPPADDING',(0,0),(-1,-1),8),('BOTTOMPADDING',(0,0),(-1,-1),8),
    ]))
    story.append(tab)
def code(text):
    story.append(Preformatted(text.strip(),styles['code']))
def page(): story.append(PageBreak())
def statusbox(title,text):
    t=Table([[para(title,'h2')],[para(text,'body')]],colWidths=[17*cm])
    t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),LIGHT),('BOX',(0,0),(-1,-1),0.7,TEAL),('LEFTPADDING',(0,0),(-1,-1),13),('RIGHTPADDING',(0,0),(-1,-1),13),('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),6)]))
    story.append(t)

add('FIAP  /  CIDADES ESG INTELIGENTES', 'label')
story.append(Spacer(1,1.1*cm))
add('HydroGuard','title')
add('CI/CD, containerização\ne orquestração de ambientes','h1')
add('API de monitoramento de consumo de água com indicadores ESG, cadastro de medidores, relatórios e alertas de possíveis vazamentos.')
story.append(Spacer(1,0.5*cm))
add('Integrantes','h2')
add((ROOT/'docs/integrantes.txt').read_text().strip())
add('Objetivo da atividade','h2')
add('Automatizar build, testes e deploy; empacotar a aplicação em containers; orquestrar API e banco; documentar arquitetura e evidências de staging e produção.')
statusbox('Situação: implementação preparada; execução externa pendente',
          'Os testes estão concentrados em C# e foram executadas somente verificações estáticas nesta revisão. O ambiente de preparação não tem .NET nem Docker. Não houve execução do GitHub Actions, publicação de imagem ou deploy externo. Os prints obrigatórios e os nomes/RMs precisam ser acrescentados antes da entrega final.')
add('Escopo ESG','h2')
add('Ambiental: apoiar identificação de consumo elevado e desperdício de água. Social: facilitar acesso a informações por uma interface web. Governança: autenticação, configuração externa de segredos e rastreabilidade por commit e digest. Não foram medidos ganhos ambientais ou validados indicadores como certificação ESG.','small')
page()

heading(1,'Pipeline CI/CD')
add('GitHub Actions coordena o fluxo. GitHub Container Registry armazena a imagem. Os jobs de CI usam Ubuntu hospedado pelo GitHub; deploys usam runners Linux x64 persistentes nos hosts dos ambientes.')
table([
 ['Etapa','Lógica e condição de avanço'],
 ['1. Build e testes','Restore, build Release, 20 testes C# com xUnit. Publica TRX/cobertura. Falha bloqueia imagem e deploy.'],
 ['2. Container e smoke','Constrói imagem e sobe Compose com SQL real. Valida readiness, frontend, Swagger, autenticação e rotas medidores/ESG.'],
 ['3. Publicação GHCR','Somente main: publica a imagem validada com tag do commit e obtém digest SHA-256.'],
 ['4. Staging','Pull por digest, Compose persistente e smoke validando Staging + revisão. Produção depende do sucesso.'],
 ['5. Produção','Promove o MESMO digest sem recompilar. Smoke valida Production + revisão.'],
])
add('Gatilhos e política','h2')
add('Pull requests: validação de CI sem publicação/deploy. Push em main ou execução manual em main: fluxo completo. Uma execução por branch evita deploys simultâneos. Produção avança automaticamente após staging; revisores obrigatórios podem ser adicionados se a política mudar.')
add('Separar CI de ambientes persistentes','h2')
add('A stack hydroguard-ci é temporária e removida ao fim do job. Ela não é evidência de staging. Os projetos hydroguard-staging e hydroguard-production continuam em execução nos hosts após o job.')
add('Artifacts gerados após execução real','h2')
add('test-results: TRX e cobertura. container-evidence: smoke e digest. staging-evidence e production-evidence: smoke, estado dos containers e revisão. Nesta versão esses artifacts externos ainda não existem.','small')
page()

heading(2,'Docker e arquitetura')
add('Dois serviços por ambiente: API ASP.NET Core, que também serve o frontend, e SQL Server 2022 Express. A aplicação escuta 8080 dentro do container; a porta do host distingue os ambientes.')
table([
 ['Recurso','Configuração'],
 ['Imagem da aplicação','Multi-stage: SDK 8 para restore/publish; ASP.NET 8 bookworm-slim para runtime. Inclui curl para health check; executa como usuário app.'],
 ['Banco','SQL Server 2022 Express, acessível somente pela rede interna Docker; porta 1433 não publicada no host.'],
 ['Persistência','Volume sqlserver_data com prefixo do projeto Compose; dados sobrevivem à recriação de containers.'],
 ['Redes','frontend para a API e database interna compartilhada por API/banco; redes diferentes por projeto.'],
 ['Inicialização','SQL passa health check; API aplica migrations e cria admin inicial. API saudável exige conexão ao banco.'],
 ['Variáveis','ConnectionStrings, Jwt e Bootstrap recebidas em runtime. Secrets separados por ambiente; não entram na imagem.'],
])
add('Ambientes isolados','h2')
table([
 ['Ambiente','Projeto Compose / porta / seed'],
 ['Local','hydroguard-local / 5000 / dados de demonstração habilitados'],
 ['Staging','hydroguard-staging / 5001 / somente usuário admin'],
 ['Produção','hydroguard-production / 5000 / somente usuário admin'],
])
add('Identificação da imagem','h2')
code('Tag: ghcr.io/<proprietario>/<repositorio>:<commit>\nDeploy: ghcr.io/<proprietario>/<repositorio>@sha256:<digest>')
add('O digest real será conhecido após publicação. /healthz retorna ambiente e revisão do commit; /livez indica apenas que o processo responde. Imagens-base e SQL usam tags móveis nesta versão. Fixar seus digests é uma evolução para reprodutibilidade integral.','small')
page()

heading(3,'Execução e preparação dos hosts')
add('Execução local','h2')
code('python3 scripts/setup_env.py\ndocker compose -p hydroguard-local config --quiet\ndocker compose -p hydroguard-local up -d --build \\\n  --wait --wait-timeout 300\ndocker compose -p hydroguard-local ps')
add('Acesse http://localhost:5000 e /swagger. Entre como admin usando ADMIN_PASSWORD do .env gerado. No Windows, use python quando python3 não estiver disponível. Para parar preservando dados: docker compose -p hydroguard-local down.')
add('Testes de integração','h2')
code('dotnet restore HydroGuard.sln\ndotnet build HydroGuard.sln -c Release --no-restore\ndotnet test tests/HydroGuard.Tests/HydroGuard.Tests.csproj -c Release --no-build')
add('SDK .NET 8 é necessário para xUnit e smoke C#; o pipeline prepara o SDK nos jobs. Há 20 testes xUnit e um executável smoke C# sem pacotes externos. InMemory não prova comportamento relacional: a etapa container usa SQL Server real. Python foi removido dos testes e do pipeline; permanece apenas nos geradores opcionais de .env/PDF.')
add('Preparação do GitHub e ambientes','h2')
for text in [
 '1. Publique o projeto em repositório GitHub com main e Environments disponíveis. Crie staging e production e limite deployments à main.',
 '2. Nos hosts Linux x64, instale Docker, Compose v2.24+, Bash e Git; o workflow prepara o SDK .NET 8. Registre runners usando os comandos de Settings > Actions > Runners.',
 '3. Atribua labels hydroguard-staging e hydroguard-production. Instale runners como serviços. Em um host único, use dois processos/pastas e recursos para duas stacks.',
 '4. Em cada environment, configure secrets MSSQL_SA_PASSWORD, JWT_KEY e ADMIN_PASSWORD. Use valores diferentes. Configure variables API_PORT, BIND_ADDRESS e APP_URL.',
 '5. Faça push em main, acompanhe os quatro jobs e acesse ambos os ambientes. APP_URL cria apenas um link; domínio, proxy HTTPS ou túnel devem ser preparados no host.',
]: add(text,'small')
add('O README detalha cada passo e acesso ao GHCR por GITHUB_TOKEN. Senhas do SQL/admin devem ter 12+ caracteres; JWT deve ter 32+ bytes. BIND_ADDRESS padrão é 127.0.0.1.','small')
page()

heading(4,'Evidências verificadas nesta preparação')
add('Verificações estáticas da revisão com testes C#','h2')
add('O registro abaixo foi produzido por verificações reais de arquivos, sintaxe Bash, YAML e referências de projetos. Como não há SDK .NET ou Docker aqui, nenhum teste C# nem smoke HTTP foi executado. Esse registro não comprova funcionamento da API ou dos deploys.','small')
log=(ROOT/'evidence/validacao-local.txt').read_text()
# Preserva o conteúdo do log real, quebrando linhas para caber na página.
wrapped=[]
for line in log.splitlines():
    wrapped.extend(textwrap.wrap(line, width=100, replace_whitespace=False, drop_whitespace=False) or [''])
code('\n'.join(wrapped))
add('Arquivo completo: evidence/validacao-local.txt. O ZIP inclui esse registro. Nenhum resultado .NET/Docker foi inferido a partir dessas verificações.','small')
page()

heading(5,'Prints obrigatórios: captura pendente')
add('Pipeline com build, testes e deploy','h2')
statusbox('PENDENTE - execução GitHub Actions',
          'Capturar run real com build-test, container, deploy-staging e deploy-production aprovados. Incluir logs de build/testes, resultado xUnit, commit e digest da imagem. Registrar URL da run em docs/evidencias.md.')
story.append(Spacer(1,0.3*cm))
add('Staging funcionando','h2')
statusbox('PENDENTE - ambiente staging',
          'Capturar interface acessível no host de staging, containers saudáveis e /healthz retornando Staging + revisão do commit. Baixar staging-evidence. O nome do GitHub Environment não comprova funcionamento.')
story.append(Spacer(1,0.3*cm))
add('Produção funcionando','h2')
statusbox('PENDENTE - ambiente de produção',
          'Capturar interface de produção, containers saudáveis e /healthz retornando Production + a mesma revisão. Confirmar que o digest da API coincide com staging; baixar production-evidence.')
add('Como incorporar evidências ao documento','h2')
add('Adicione imagens reais em docs/prints/pipeline.png, staging.png e production.png. Atualize nomes/RMs em docs/integrantes.txt e links em docs/evidencias.md. Execute pip install -r docs/requirements.txt e python3 docs/generate_pdf.py. O gerador inclui as imagens disponíveis antes do checklist final. Atualize os textos e o checklist para refletir os resultados reais; acrescentar uma imagem não muda automaticamente o status.','small')
add('Não exponha .env, senhas, tokens ou secrets nos prints. Use config --quiet e compose ps. Teste a URL pública separadamente quando houver proxy: o smoke automatizado usa a porta local do host.','small')
page()

heading(6,'Desafios e decisões técnicas')
table([
 ['Desafio','Solução e limite'],
 ['Ausência de SDK/Docker','Pipeline preparado para executar em runners com ferramentas. Execução completa continua pendente; evidências não foram fabricadas.'],
 ['Segredos fixos','Removidos do código/configuração. Geração aleatória local e secrets de environment. Admin inicial criado por Bootstrap.'],
 ['Testes com providers conflitantes','SQL não registrado em Testing; factory registra InMemory com nome único. Importação de Hosting acrescentada para as extensões de teste. Validação xUnit pendente.'],
 ['Ordem de inicialização','Health check SQL com sqlcmd, depends_on service_healthy e readiness API com conexão real.'],
 ['Colisão entre ambientes','Sem nomes fixos de container; projetos, portas, volumes e redes separados.'],
 ['Rastreabilidade de releases','GHCR mantido. Commit na imagem e deploy por digest; smoke C# confirma ambiente e revisão.'],
])
add('Limites operacionais','h2')
add('Uma réplica da API por stack, migrations no startup e possibilidade de breve indisponibilidade ao atualizar. Sem rollback automático, backups automáticos ou alta disponibilidade. Produção com dados reais exige evolução da gestão de permissões SQL, TLS, observabilidade e recuperação.')
add('Rollback e persistência','h2')
add('Reaplique o digest anterior usando scripts/deploy.sh e a revisão correspondente, com os mesmos secrets do ambiente. Reverter imagem não reverte schema. Não use down --volumes em staging/produção. Mudanças de secret não trocam automaticamente senhas já armazenadas no banco.')
add('Referências oficiais','h2')
for title,url in [
 ('GitHub Actions: deploy','https://docs.github.com/en/actions/how-tos/deploy/configure-and-manage-deployments/control-deployments'),
 ('Docker Compose: ordem de inicialização','https://docs.docker.com/compose/how-tos/startup-order/'),
 ('Microsoft: SQL Server em containers','https://learn.microsoft.com/en-us/sql/linux/quickstart-install-connect-docker?view=sql-server-ver16'),
]:
    story.append(Paragraph(escape(title)+': <link href="'+escape(url)+'" color="#078879">documentação oficial</link>',styles['small']))
page()

# Adiciona apenas imagens fornecidas, nunca cria prints simulados.
for filename,title in [('pipeline.png','Pipeline CI/CD'),('staging.png','Ambiente staging'),('production.png','Ambiente produção')]:
    file=ROOT/'docs/prints'/filename
    if file.exists():
        heading(7,'Evidência adicionada: '+title)
        add('Imagem fornecida em docs/prints/'+filename+'. Consulte docs/evidencias.md para URL, commit e contexto. A imagem não altera automaticamente as pendências do checklist.','small')
        im=Image(str(file));im._restrictSize(17*cm,21*cm);story.append(im);page()

heading(7,'Checklist de entrega')
add('Preenchido de acordo com o que está comprovado nesta versão. Arquivo implementado não significa execução aprovada. Atualize após os deploys reais.','small')
table([
 ['Item obrigatório','Situação nesta versão'],
 ['Projeto ZIP organizado e completo','PREPARADO - inclui código, configs, scripts e documentação.'],
 ['Dockerfile funcional','IMPLEMENTADO - execução funcional ainda não comprovada.'],
 ['Docker Compose / Kubernetes','COMPOSE IMPLEMENTADO - volume, variáveis e redes; execução pendente.'],
 ['Pipeline build, teste e deploy','CONFIGURADO - GitHub Actions com dois deploys; run externa pendente.'],
 ['README com instruções e prints','INSTRUÇÕES PRONTAS - prints/links externos pendentes.'],
 ['PDF/PPT técnico com evidências','PDF PREPARADO - inclui log local; faltam prints externos obrigatórios.'],
 ['Deploy realizado em staging','PENDENTE - requer host/runner, secrets e execução real.'],
 ['Deploy realizado em produção','PENDENTE - depende de staging aprovado e execução real.'],
 ['Integrantes e RMs','PENDENTE - nomes completos e RMs não informados.'],
])
add('Verificações adicionais','h2')
add('[OK] Testes Python removidos; smoke migrado para C#; sintaxe Bash e análise YAML verificadas.\n[PENDENTE] Build .NET, 20 testes xUnit, build Docker e validação Compose real.\n[PENDENTE] Imagem GHCR publicada e mesma referência usada nos dois ambientes.\n[PENDENTE] Artifacts e prints reais adicionados ao README/PDF.','small')
statusbox('A entrega final ainda depende das execuções externas',
          'Este documento registra uma implementação preparada. Para cumprir integralmente a atividade, execute o pipeline e os dois deploys, acrescente as evidências reais e atualize os itens pendentes.')


def footer(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(colors.HexColor('#D6E3E7'));canvas.line(2*cm,1.65*cm,19*cm,1.65*cm)
    canvas.setFont(FONT,7);canvas.setFillColor(INK)
    canvas.drawString(2*cm,1.2*cm,'HydroGuard | FIAP | CI/CD e Docker | Execuções externas pendentes')
    canvas.drawRightString(19*cm,1.2*cm,str(doc.page))
    canvas.restoreState()

doc=SimpleDocTemplate(str(OUT),pagesize=(21*cm,29.7*cm),leftMargin=2*cm,rightMargin=2*cm,topMargin=1.9*cm,bottomMargin=2.1*cm,title='HydroGuard - Documentação CI/CD e Docker',author='Integrantes a preencher')
doc.build(story,onFirstPage=footer,onLaterPages=footer)
print(OUT)
