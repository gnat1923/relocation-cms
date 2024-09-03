from typing import Optional, List
import sqlalchemy as sa
import sqlalchemy.orm as so
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db, login

@login.user_loader
def load_user(id):
    return db.session.get(User, int(id))

class User(UserMixin, db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    username: so.Mapped[str] = so.mapped_column(sa.String(64), index=True, unique=True)
    email: so.Mapped[str] = so.mapped_column(sa.String(120), index=True, unique=True)
    password_hash: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256))

    def __repr__(self):
        return "<User {}>".format(self.username)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
class Company(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    name: so.Mapped[str] = so.mapped_column(sa.String(100), index=True, unique=True)
    contact: so.Mapped[str] = so.mapped_column(sa.String(256))
    notes: so.Mapped[Optional[str]] = so.mapped_column(sa.String(1064))

    # Relationships
    assignees: so.Mapped[List["Assignee"]] = so.relationship(back_populates="company")
    company_packages: so.Mapped[List["CompanyPackage"]] = so.relationship(back_populates="company")

    def __repr__(self):
        return "<Company {}>".format(self.name)


class Package(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    name: so.Mapped[str] = so.mapped_column(sa.String(100), index=True, unique=True)
    description: so.Mapped[Optional[str]] = so.mapped_column(sa.String(500))

    # Relationships
    company_packages: so.Mapped[List["CompanyPackage"]] = so.relationship(back_populates="package")
    assignees: so.Mapped[List["Assignee"]] = so.relationship(
        secondary="assignee_package",
        back_populates="packages"
    )

    def __repr__(self):
        return "<Package {}>".format(self.name)
    
class CompanyPackage(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    company_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey("company.id"))
    package_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey("package.id"))
    price: so.Mapped[float] = so.mapped_column(sa.Float)

    # Relationships
    company: so.Mapped["Company"] = so.relationship(back_populates="company_packages")
    package: so.Mapped["Package"] = so.relationship(back_populates="company_packages")

    def __repr__(self):
        package_name = self.package.name if self.package else "Unknown Package"
        company_name = self.company.name if self.company else "Unknown Company"
        return f"<CompanyPackage {package_name} for {company_name}: €{self.price}>"
    
# New association table for Assignee and Package
assignee_package = sa.Table(
    "assignee_package",
    db.metadata,
    sa.Column("assignee_id", sa.Integer, sa.ForeignKey("assignee.id")),
    sa.Column("package_id", sa.Integer, sa.ForeignKey("package.id"))
)


class Assignee(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    name: so.Mapped[str] = so.mapped_column(sa.String(100), index=True)
    origin_country: so.Mapped[str] = so.mapped_column(sa.String(100), index=True)
    destination_city: so.Mapped[str] = so.mapped_column(sa.String(100), index=True)
    company_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey("company.id"))

    # Relationships
    company: so.Mapped["Company"] = so.relationship(back_populates="assignees")
    packages: so.Mapped[List["Package"]] = so.relationship(
        secondary="assignee_package",
        back_populates="assignees"
    )

    def __repr__(self):
        return "<Assignee {} from {}>".format(self.name, self.company.name)
    

