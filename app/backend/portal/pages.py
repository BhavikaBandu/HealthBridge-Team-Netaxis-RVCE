"""HTML pages for the patient and doctor portals. Data is loaded by page scripts from the JSON API."""
import uuid

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from backend.config import ROOT
from .deps import get_db, load_session
from .models import DoctorProfile, PatientProfile, TripReport

router = APIRouter(include_in_schema=False)
templates = Jinja2Templates(directory=str(ROOT / 'frontend/templates'))
ASSET_VERSION = '33'

PATIENT_NAV = [('dashboard', '/dashboard', 'Dashboard', 'house'), ('profile', '/profile', 'My Profile', 'person'),
               ('trips', '/trips', 'My Trips', 'airplane'), ('history', '/medical-history', 'Medical History', 'heart-pulse'),
               ('documents', '/documents', 'Documents', 'file-earmark-text'),
               ('travel', '/travel-summary', 'Travel Health Summary', 'clipboard2-pulse'),
               ('access', '/doctor-access', 'Doctor Access', 'shield-lock')]
DOCTOR_NAV = [('d_dashboard', '/doctor/dashboard', 'Dashboard', 'house'), ('d_profile', '/doctor/profile', 'My Profile', 'person'),
              ('d_patients', '/doctor/patients', 'Patient Records', 'people'),
              ('d_knowledge', '/doctor/knowledge', 'Knowledge Explorer', 'journal-medical')]
PAGES = {'dashboard': ('Dashboard', ''), 'travel': ('Travel Health Summary', 'What your records mean for your destination'), 'profile': ('My Profile', 'Manage your personal information'),
         'trips': ('My Trips', 'Manage your travel plans and care journeys'),
         'history': ('Medical History', 'Maintain your health records in a structured format'),
         'documents': ('Documents', 'Upload and manage your medical files'),
         'access': ('Doctor Access', 'Choose which doctors can view your records'),
         'd_dashboard': ('Dashboard', ''), 'd_profile': ('My Profile', 'Manage your professional information'),
         'd_patients': ('Patient Records', 'Find patients, request access and view their medical records'),
         'd_knowledge': ('Knowledge Explorer', 'Search trusted, country-specific medical knowledge')}
HOME = {'patient': '/dashboard', 'doctor': '/doctor/dashboard'}


def _render(request, template, **ctx):
    return templates.TemplateResponse(request, template, {'v': ASSET_VERSION, **ctx})


@router.get('/')
def root(request: Request, db: Session = Depends(get_db)):
    auth = load_session(db, request)
    return RedirectResponse(HOME.get(auth.user.role, '/login') if auth else '/login', status_code=303)


def _auth_page(template):
    def view(request: Request, db: Session = Depends(get_db)):
        auth = load_session(db, request)
        if auth and auth.user.role in HOME:
            return RedirectResponse(HOME[auth.user.role], status_code=303)
        return _render(request, template)
    return view


router.add_api_route('/login', _auth_page('portal/login.html'), methods=['GET'], response_class=HTMLResponse)
router.add_api_route('/signup', _auth_page('portal/signup.html'), methods=['GET'], response_class=HTMLResponse)
router.add_api_route('/doctor/signup', _auth_page('portal/doctor_signup.html'), methods=['GET'], response_class=HTMLResponse)


def _app_page(page, template, role):
    def view(request: Request, db: Session = Depends(get_db)):
        auth = load_session(db, request)
        if not auth:
            return RedirectResponse('/login', status_code=303)
        if auth.user.role != role:
            return RedirectResponse(HOME.get(auth.user.role, '/login'), status_code=303)
        title, subtitle = PAGES[page]
        if role == 'doctor':
            d = db.get(DoctorProfile, auth.user.id)
            ctx = dict(nav=DOCTOR_NAV, id_label='Doctor ID', public_id=d.public_doctor_id if d else '',
                       full_name=d.full_name if d else '', verification_status=d.verification_status if d else 'pending',
                       profile_url='/doctor/profile')
        else:
            p = db.get(PatientProfile, auth.user.id)
            ctx = dict(nav=PATIENT_NAV, id_label='Patient ID', public_id=auth.user.public_patient_id,
                       full_name=p.full_name if p else '', profile_url='/profile')
        return _render(request, template, page=page, title=title, subtitle=subtitle, email=auth.user.email, **ctx)
    return view


for _page, _path, *_ in PATIENT_NAV:
    router.add_api_route(_path, _app_page(_page, f'portal/{_page}.html', 'patient'), methods=['GET'], response_class=HTMLResponse)
for _page, _path, *_ in DOCTOR_NAV:
    router.add_api_route(_path, _app_page(_page, f'doctor/{_page[2:]}.html', 'doctor'), methods=['GET'], response_class=HTMLResponse)


@router.get('/knowledge')
def knowledge_redirect():
    return RedirectResponse('/doctor/knowledge', status_code=303)


@router.get('/travel-summary/report/{report_id}')
def travel_report(report_id: uuid.UUID, request: Request, db: Session = Depends(get_db)):
    """Printable travel health report (black and white). Only the patient who owns it can open it."""
    auth = load_session(db, request)
    if not auth:
        return RedirectResponse('/login', status_code=303)
    r = db.get(TripReport, report_id)
    if r is None or auth.user.role != 'patient' or r.patient_id != auth.user.id:
        raise HTTPException(404, 'Report not found')
    return _render(request, 'portal/report_print.html', r=r.content, auto_print=request.query_params.get('print') == '1')


@router.get('/doctor/patients/{code}/report/{report_id}')
def doctor_report(code: str, report_id: uuid.UUID, request: Request, db: Session = Depends(get_db)):
    """Printable complete patient report. Only for the doctor who generated it, while access is granted."""
    from .routers.doctor import granted_patient
    auth = load_session(db, request)
    if not auth:
        return RedirectResponse('/login', status_code=303)
    if auth.user.role != 'doctor':
        raise HTTPException(404, 'Report not found')
    u = granted_patient(db, auth, code)   # raises if access was revoked
    r = db.get(TripReport, report_id)
    if r is None or r.audience != 'doctor' or r.patient_id != u.id or r.content.get('_doctor_id') != str(auth.user.id):
        raise HTTPException(404, 'Report not found')
    return _render(request, 'portal/report_print.html', r=r.content, auto_print=request.query_params.get('print') == '1')
