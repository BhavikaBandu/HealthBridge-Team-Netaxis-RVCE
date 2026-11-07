"""Developer/admin tool to review doctor accounts (prototype verification step).

    python -m backend.portal.doctors list
    python -m backend.portal.doctors approve doctor@example.com
    python -m backend.portal.doctors reject doctor@example.com

A typed registration number is NOT proof of qualification; approve only after checking it yourself.
"""
import argparse

from sqlalchemy import select

from backend.database import SessionLocal
from backend.models import now
from .models import DoctorProfile, User


def main():
    ap = argparse.ArgumentParser(description='Review doctor accounts')
    ap.add_argument('action', choices=['list', 'approve', 'reject'])
    ap.add_argument('email', nargs='?')
    args = ap.parse_args()
    with SessionLocal() as s:
        if args.action == 'list':
            for u, d in s.execute(select(User, DoctorProfile).join(DoctorProfile, DoctorProfile.user_id == User.id)
                                  .order_by(User.created_at)):
                print(f'{d.verification_status:9} {d.public_doctor_id:12} {u.email:40} reg: {d.registration_number or "-"}')
            return
        if not args.email:
            ap.error('email is required')
        u = s.scalar(select(User).where(User.email == args.email.strip().lower(), User.role == 'doctor'))
        if not u:
            raise SystemExit(f'No doctor account with email {args.email}')
        d = s.get(DoctorProfile, u.id)
        d.verification_status = 'approved' if args.action == 'approve' else 'rejected'
        d.verified_at = now() if args.action == 'approve' else None
        s.commit()
        print(f'{d.public_doctor_id} {u.email} -> {d.verification_status}')


if __name__ == '__main__':
    main()
