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

    countries_list = []
    with open("app/static/countries.txt", "r") as f:
        for country in f:
            countries_list.append(country.strip())

    german_city_list = []
    with open("app/static/german_cities.txt", "r") as f:
        for city in f:
            german_city_list.append(city.strip())

    form.origin_country.choices = [(country, country) for country in countries_list]
    form.destination_city.choices = [(city, city) for city in german_city_list]

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

@app.route("/assignees", methods=["GET"])
@login_required
def assignees():
    assignees = Assignee.query.order_by(Assignee.create_date).all()

    return render_template("assignees.html", assignees=assignees)

@app.route("/assignees/<assignee_id>", methods=["GET"])
@login_required
def view_assignee(assignee_id):
    assignee = db.first_or_404(sa.select(Assignee).where(Assignee.id == assignee_id))

    return render_template("view_assignee.html", title=f"View Assignee - {assignee.name}", assignee=assignee)

@app.route("/assignees/edit/<assignee_id>", methods=["GET", "POST"])
@login_required
def edit_assignee(assignee_id):
    assignee = db.first_or_404(sa.select(Assignee).where(Assignee.id == assignee_id))
    form = NewAssigneeForm()

    #import lists
    countries_list = []
    with open("app/static/countries.txt", "r") as f:
        for country in f:
            countries_list.append(country.strip())

    german_city_list = []
    with open("app/static/german_cities.txt", "r") as f:
        for city in f:
            german_city_list.append(city.strip())

    form.origin_country.choices = [(country, country) for country in countries_list]
    form.destination_city.choices = [(city, city) for city in german_city_list]

    if request.method == "GET":
    #populate the form
        form.name.data = assignee.name
        form.origin_country.data = assignee.origin_country 
        form.destination_city.data = assignee.destination_city 
        form.company.data = assignee.company

    if form.validate_on_submit() and request.method == "POST":
        try:
            #update db data
            assignee.name = form.name.data
            assignee.origin_country = form.origin_country.data
            assignee.destination_city = form.destination_city.data
            assignee.company_id = form.company.data

            #commit to db
            db.session.commit()
            flash("Assignee successfully updated")
            return redirect(url_for("assignees"))

        except Exception as e:
            db.session.rollback()
            flash(f"An error occured: {str(e)}", "error")
            return redirect(url_for("assignees"))
            

    return render_template("edit_assignee.html", title=f"Edit Assignee - {assignee.name}", form=form, assignee=assignee)

@app.route("/accounting")
@login_required
def accounting():
    return render_template("accounting.html")    

@app.route("/packages", methods=["GET"])
@login_required
def packages():
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

        package_id_list = request.form.getlist('package_id') #pull package_ids from request.form
        try:
            company = Company(
                name = form.name.data,
                contact = form.contact.data,
                notes = form.notes.data,
                address1 = form.address1.data,
                address2 = form.address2.data,
                postcode = form.postcode.data,
                city = form.city.data
            )

            db.session.add(company)
            db.session.commit() # Flush to get the company ID for the relationships

            package_id_counter = 0
            for filled_package_form in form.packages:
                '''print("See package form:")
                print(f"Package ID submitted: {filled_package_form.package_id.data}")
                print(f"Price submitted: {filled_package_form.price.data}")'''
                    
                company_package = CompanyPackage(
                    company_id = company.id,
                    package_id = int(package_id_list[package_id_counter]),
                    price = filled_package_form.price.data               
                )
                package_id_counter += 1
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

@app.route("/companies/edit/<company_name>", methods=["GET", "POST"])
@login_required
def edit_company(company_name):
    company = db.first_or_404(sa.select(Company).where(Company.name == company_name))
    packages = db.session.execute(
        sa.select(CompanyPackage).where(CompanyPackage.company_id == company.id)
        ).scalars().all()
    form = NewCompanyForm()

    if request.method == "GET":
        # Fetch all packages from db
        #packages = Package.query.all() sorted above
        for package in packages:
            package_form = PackagePriceForm()
            package_form.package_id.data = package.id
            package_form.package_name.data = package.package.name
            package_form.price = package.price
            form.packages.append_entry(package_form)

        #populate the entry fields
        form.name.data = company.name
        form.contact.data = company.contact
        form.address1.data = company.address1
        form.address2.data = company.address2
        form.postcode.data = company.postcode
        form.city.data = company.city
        form.notes.data = company.notes

        #load up company packages
        company_packages_get = db.session.execute(
                    sa.select(CompanyPackage)
                    .where(CompanyPackage.company_id == company.id)
                ).scalars().all()
        
        pprint.pp(company_packages_get)

    if form.validate_on_submit():
        package_id_list = request.form.getlist('package_id') #pull package_ids from request.form
        pprint.pp(package_id_list)

        company_packages_get = db.session.execute(
                    sa.select(CompanyPackage)
                    .where(CompanyPackage.company_id == company.id)
                ).scalars().all()
        try:
            company.name = form.name.data
            company.contact = form.contact.data
            company.address1 = form.address1.data
            company.address2 = form.address2.data
            company.postcode = form.postcode.data
            company.city = form.city.data
            company.notes = form.notes.data

            package_price_list = []
            for package in form.packages:
                package_price_list.append(package.price.data)

            i = 0
            for company_package in company_packages_get:
                company_package.price = package_price_list[i]
                i += 1
            
            db.session.commit()
            flash("Company and package prices successfully updated")
            return redirect(url_for("companies"))
        
        except Exception as e:
            db.session.rollback()
            flash(f"An error occured: {str(e)}", "error")
            return redirect(url_for("companies"))

    return render_template("edit_company.html", company=company, form=form)

@app.route("/companies/company_packages", methods=["GET"])
@login_required
def view_company_packages():
    # This function has taught me that my package id's are not being correctly assigned to company packages. It can probably be deleted later
    comp_packages = CompanyPackage.query.all()
    comp_names = []
    
    for company in Company.query.all():
        comp_names.append(company.name)
    
    packages = Package.query.all()
    return render_template("company_package.html", packages=packages, comp_packages=comp_packages, comp_names=comp_names)

