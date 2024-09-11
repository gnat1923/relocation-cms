from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user, login_required
from urllib.parse import urlsplit
import sqlalchemy as sa
import pprint
from app import app, db
from app.forms import LoginForm, RegistrationForm, NewAssigneeForm, NewCompanyForm, NewPackageForm, PackagePriceForm
from app.models import User, Assignee, Company, Package, CompanyPackage

@app.route("/")
@app.route("/index")
@login_required
def index():
    posts = [
        {
            'author': {'username': 'John'},
            'body': 'Beautiful day in Portland!'
        },
        {
            'author': {'username': 'Susan'},
            'body': 'The Avengers movie was so cool!'
        }
    ]
    return render_template("index.html", title="Home", posts=posts)

@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.scalar(
            sa.select(User).where(User.username == form.username.data)
        )
        if user is None or not user.check_password(form.password.data):
            flash("Invalid username or password")
            return url_for("login")
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get("next")
        if not next_page or urlsplit(next_page).netloc != "":
            next_page = url_for("index")
        return redirect(next_page)

    return render_template("login.html", title="Sign In", form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("index"))

@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash("Congratulations, you are now a registered user!")
        return redirect(url_for("login"))
    return render_template("register.html", title="Register", form=form)

@app.route("/newassignee", methods=["POST", "GET"])
@login_required
def new_assignee():
    form = NewAssigneeForm()
    if form.validate_on_submit():
        assignee = Assignee(name=form.name.data,
                            origin_country=form.origin_country.data,
                            destination_city=form.destination_city.data,
                            company_id = form.company.data
                            )
        print(form.data)
        db.session.add(assignee)
        db.session.commit()
        flash("Assignee successfully added")
        redirect(url_for("index"))

    return render_template("new_assignee.html", title="New Assignee", form=form)

@app.route("/accounting")
@login_required
def accounting():
    return render_template("accounting.html")

@app.route("/packages", methods=["GET"])
@login_required
def packages():
    '''packages = [
        {"name":"8hr", "description":"An 8 hour relocation package"},
        {"name":"12hr", "description":"A 12 hour relocation package"},
        {"name":"20hr", "description":"A 20 hour relocation package"},
        {"name":"40hr", "description":"A 40 hour relocation package"},
        {"name":"Visa", "description":"Assist assignee with visa application"},
        {"name":"VWP", "description":"Assist assignee with visa and work permit application"},
        {"name":"F(V)", "description":"Assist assignee's family with visa application"},
        {"name":"F(VWP)", "description":"Assist assignee' family with visa and work permit application"},
        {"name":"AW", "description":"Assist an asignee already in Germany with changing their employer"}
    ]'''
    packages = Package.query.all()
    return render_template("packages.html", title="Packages", packages=packages)

@app.route("/packages/add_package", methods=["GET", "POST"])
@login_required
def add_package():
    form = NewPackageForm()
    if form.validate_on_submit():
        package_name = form.name.data
        package_description = ""
        if form.description.data:
            package_description = form.description.data
        
        package = Package(
            name = package_name,
            description = package_description
        )
        db.session.add(package)
        db.session.commit()
        flash("Package successfully added")
        return redirect(url_for("packages"))

    return render_template("add_package.html", title="Add Package", form=form)

@app.route("/companies", methods=["GET"])
@login_required
def companies():
    companies = Company.query.all()
    '''[
        {"name":"Facebook"},
        {"name": "Apple"},
        {"name": "Amazon"},
        {"name": "Netflix"},
        {"name": "Google"}
    ]'''

    return render_template("companies.html", companies=companies)

@app.route("/companies/add_company", methods=["GET", "POST"])
@login_required
def add_company():
    form = NewCompanyForm()

    #fetch all packages and send them to company form package field
    if request.method == "GET":
        # Fetch all packages from db
        packages = Package.query.all()
        for package in packages:
            package_form = PackagePriceForm()
            package_form.package_id.data = package.id
            package_form.package_name.data = package.name
            package_form.price = None
            form.packages.append_entry(package_form)
            

    #submit the company section of the form
    if form.validate_on_submit() and request.method == "POST":
        try:
            company = Company(
                name = form.name.data,
                contact = form.contact.data,
                notes = form.notes.data
            )

            db.session.add(company)
            db.session.commit() # Flush to get the company ID for the relationships


            #pull the price for each package and send to db
            #this function is sending a flase package_id <input id= - why?
            for filled_package_form in form.packages:
                print("See package form:")
                for i in filled_package_form:
                    print(i)
                    
                company_package = CompanyPackage(
                    company_id = company.id,
                    package_id = request.form.get("package_id"),
                    price = filled_package_form.price.data               
                )
                db.session.add(company_package)
            

            db.session.commit()
            flash("Company and package prices successfully added")
            return redirect(url_for("companies"))
        
        except Exception as e:
            db.session.rollback()
            flash(f"An error occured: {str(e)}", "error")
            return redirect(url_for("companies"))

    elif request.method == "POST":
        flash("There were errors in your submission. Please check the form and try again.", "error")
    

    
    return render_template("add_company.html", title="Add New Company", form=form)

@app.route("/companies/<company_name>")
@login_required
def view_company(company_name):
    company = db.first_or_404(sa.select(Company).where(Company.name == company_name))

    return render_template("view_company.html", title=f"Company Info - {company.name}", company=company)

@app.route("/companies/company_packages", methods=["GET"])
@login_required
def view_company_packages():
    # This function has taught me that my package id's are not being correctly assigned to company packages. It can probably be deleted later
    packages = CompanyPackage.query.all()
    #print(packages)
    return render_template("company_package.html", packages=packages)
