from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user, login_required
from urllib.parse import urlsplit
import sqlalchemy as sa
import pprint
import plotly.graph_objs as go
import plotly.io as pio
from app import app, db
from app.forms import LoginForm, RegistrationForm, NewAssigneeForm, AssigneePackageForm, NewCompanyForm, NewPackageForm, PackagePriceForm
from app.models import User, Assignee, Company, Package, CompanyPackage

@app.route("/")
@app.route("/index")
@login_required
def index():
    #define case summary
    case_count_list = [
        {"case_type":"VMS", "count":15},
        {"case_type":"RMS", "count":10},
        {"case_type":"GMS", "count":8}
    ]
    
    total_case_count = 0
    for dict in case_count_list:
        total_case_count += dict["count"]
    
    total_dict = {"case_type":"Total", "count":total_case_count}
    case_count_list.append(total_dict)

    # Reorder the list, total first
    custom_order = ["Total", "GMS", "VMS", "RMS"]
    ordered_case_count_list = sorted(case_count_list, key=lambda x: custom_order.index(x["case_type"]))

    #define pie chart data (placeholders for now)
    labels = ["VMS", "RMS", "GMS"]
    values = []

    for value in case_count_list:
        for label in labels:
            if value["case_type"] == label:
                values.append(value["count"])

    #create the pie chart
    pie_chart = go.Figure(data=[go.Pie(labels=labels, values=values)])

    #generate html for pie chart
    pie_chart_div = pio.to_html(pie_chart, full_html=False)

    
    return render_template("index.html", title="Home", ordered_case_count_list=ordered_case_count_list, pie_chart_div=pie_chart_div)

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
            return redirect(url_for("login"))
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
    assignee_form = NewAssigneeForm()
    
    countries_list = []
    with open("app/static/countries.txt", "r") as f:
        for country in f:
            countries_list.append(country.strip())

    german_city_list = []
    with open("app/static/german_cities.txt", "r") as f:
        for city in f:
            german_city_list.append(city.strip())

    packages = Package.query.where(Package.active == True).all()

    #populate dropdown menus
    assignee_form.origin_country.choices = [(country, country) for country in countries_list]
    assignee_form.nationality.choices = [(country, country) for country in countries_list]
    assignee_form.destination_city.choices = [(city, city) for city in german_city_list]

    #create package checkboxes
    for package in packages:
        assignee_package_form = AssigneePackageForm()
        assignee_package_form.package_id.data = package.id
        assignee_package_form.package_name.data = package.name
        assignee_form.assignee_packages.append_entry(assignee_package_form)

    #populate page at GET request
    if request.method =="GET":
        ...
        

    if assignee_form.validate_on_submit():
        #pprint.pp(request.form)
        try:
            '''assignee_package_list = []
            #create list of asignee packages
            for package in assignee_form.assignee_packages:
                print(f"Packagedata: {package}")
                if package.package_status == True:
                    assignee_package_list.append(Package(package.id))
            print(f"Package List: {assignee_package_list}")'''

            #create AssigneePackage Entries
            assignee_packages = []
            for assignee_package in assignee_form.assignee_packages:
                #print(assignee_package.name)
                if assignee_package.package_status.data == True:
                    print(f"Package Name: {assignee_package.package_name.data} \nID: {assignee_package.package_id.data} \nStatus: {assignee_package.package_status.data} ")
                    '''print(f"Package ID data: {assignee_package.package_id.data}\n")
                    package_id = assignee_package.package_id.data  # Extract package ID from HiddenField
                    package = Package.query.get(package_id)  # Fetch the package using the ID
                    assignee.packages.append(package)  # Add package to assignee'''
                    package_id = str(assignee_package.package_id.data)
                    value_start = package_id.find('value="') + 7  # 7 is the length of 'value="'
                    value_end = package_id.find('"', value_start)
                    package_id2 = package_id[value_start:value_end]
                    #package_id_blocks = package_id.split('value="') 
                    #package_id2 = package_id_blocks[1].removesuffix('">')
                    print(f"New package id: {package_id2}")
                    package = Package.query.get(int(package_id2))
                    assignee_packages.append(package)


            #create assignee
            assignee = Assignee(name=assignee_form.name.data,
                                nationality=assignee_form.nationality.data,
                                origin_country=assignee_form.origin_country.data,
                                destination_city=assignee_form.destination_city.data,
                                company_id = assignee_form.company.data,
                                booking_date=assignee_form.booking_date.data,
                                arrival_date=assignee_form.arrival_date.data,
                                work_start_date=assignee_form.work_start_date.data,
                                temp_flat=assignee_form.temp_flat.data,
                                spouse=assignee_form.spouse.data,
                                child=assignee_form.child.data,
                                pets=assignee_form.pets.data,
                                hub=assignee_form.hub.data,
                                hr_contact=assignee_form.hr_contact.data,
                                job_title=assignee_form.job_title.data,
                                packages=assignee_packages
                                )
        



            db.session.add(assignee)
            db.session.commit()
            flash("Assignee successfully added with packages")
            return redirect(url_for("assignees"))
        
        except Exception as e:
            #pprint.pp(request.form)
            db.session.rollback()
            flash(f"An error occured: {str(e)}", "error")
            return redirect(url_for("assignees"))


    return render_template("new_assignee.html", title="New Assignee", assignee_form=assignee_form)

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
    form.nationality.choices = [(country, country) for country in countries_list]
    form.destination_city.choices = [(city, city) for city in german_city_list]

    if request.method == "GET":
    #populate the form
        form.name.data = assignee.name
        form.origin_country.data = assignee.origin_country
        form.nationality.data = assignee.nationality 
        form.destination_city.data = assignee.destination_city 
        form.company.data = assignee.company
        form.booking_date.data = assignee.booking_date
        form.arrival_date.data = assignee.arrival_date
        form.work_start_date.data = assignee.work_start_date
        form.temp_flat.data = assignee.temp_flat
        form.spouse.data = assignee.spouse
        form.child.data = assignee.child
        form.pets.data = assignee.pets
        form.hub.data = assignee.hub
        form.hr_contact.data = assignee.hr_contact
        form.job_title.data = assignee.job_title

    if form.validate_on_submit() and request.method == "POST":
        try:
            #update db data
            assignee.name = form.name.data
            assignee.origin_country = form.origin_country.data
            assignee.destination_city = form.destination_city.data
            assignee.nationality = form.nationality.data
            assignee.company_id = form.company.data
            assignee.booking_date = form.booking_date.data
            assignee.arrival_date = form.arrival_date.data
            assignee.work_start_date = form.work_start_date.data
            assignee.temp_flat = form.temp_flat.data
            assignee.spouse = form.spouse.data
            assignee.child = form.child.data
            assignee.pets = form.pets.data
            assignee.hub = form.hub.data
            assignee.hr_contact = form.hr_contact.data
            assignee.job_title = form.job_title.data

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
    packages = Package.query.where(Package.active == True).all()
    return render_template("packages.html", title="Packages", packages=packages)

@app.route("/inactive_packages", methods=["GET"])
@login_required
def view_inactive_packages():
    packages = Package.query.where(Package.active == False).all()

    return render_template("view_packages_inactive.html", title="Inactive Packages", packages=packages)

@app.route("/packages/add_package", methods=["GET", "POST"])
@login_required
def add_package():
    form = NewPackageForm()
    if form.validate_on_submit():
        package_name = form.name.data
        package_description = ""
        package_active = form.active.data
        if form.description.data:
            package_description = form.description.data
        package_defualt_price = form.default_price.data
        
        package = Package(
            name = package_name,
            default_price = package_defualt_price,
            description = package_description,
            active = package_active
        )
        db.session.add(package)
        db.session.commit()
        flash("Package successfully added")
        return redirect(url_for("packages"))

    return render_template("add_package.html", title="Add Package", form=form)

@app.route("/packages/edit/<package_id>", methods=["GET", "POST"])
@login_required
def edit_package(package_id):
    package = db.first_or_404(sa.select(Package).where(Package.id == package_id))
    form = NewPackageForm()

    if request.method == "GET":
        #populate the form
        form.name.data = package.name
        form.default_price.data = package.default_price
        form.description.data = package.description
        form.active.data = package.active

    if form.validate_on_submit():
        try:
            package.name = form.name.data
            package.default_price = form.default_price.data
            package.description = form.description.data 
            package.active = form.active.data

            db.session.commit()
            flash("Package successfully updated")
            return redirect(url_for("packages"))

        except Exception as e:
            db.session.rollback()
            flash(f"An error occured: {str(e)}", "error")
            return redirect(url_for("packages"))
            
    return render_template("edit_package.html", title=f"Edit Package - {package.name}", form=form, package=package)

@app.route("/companies", methods=["GET"])
@login_required
def companies():
    #companies = Company.query.all()
    companies = db.session.execute(
        sa.select(Company)
        .where(Company.active == True)
        .order_by(Company.name)
    ).scalars().all()

    return render_template("companies.html", title="CMS - View All Comapnies", companies=companies)

@app.route("/companies/add_company", methods=["GET", "POST"])
@login_required
def add_company():
    form = NewCompanyForm()

    #fetch all packages and send them to company form package field
    if request.method == "GET":
        # Fetch all packages from db
        packages = Package.query.where(Package.active == True).all()
        for package in packages:
            package_form = PackagePriceForm()
            package_form.package_id.data = package.id
            package_form.package_name.data = package.name
            package_form.price = package.default_price
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
    company_packages = db.session.execute(
        sa.select(CompanyPackage).where(CompanyPackage.company_id == company.id)
        ).scalars().all()
    
    all_packages = db.session.execute(
        sa.select(Package)
        .where(Package.active == True)
        ).scalars().all()
    
    form = NewCompanyForm()

    #needs to load ALL packages, and populate the ones already in db, leaving 'new' packages blank

    if request.method == "GET":
        # Create a dict of existing company packages for quick lookup
        company_packages = {cp.package_id: cp for cp in company.company_packages}
        #print(company_packages)

        # Fetch all packages from db
        #packages = Package.query.all() sorted above
        for package in all_packages:
            package_form = PackagePriceForm()
            package_form.package_id.data = package.id
            package_form.package_name.data = package.name
            #package_form.price = package.price
            if package.id in company_packages:
                #print("True")
                package_form.price = company_packages[package.id].price
            else:
                #print("False")
                package_form.price = None
            form.packages.append_entry(package_form)

        #populate the entry fields
        form.name.data = company.name
        form.contact.data = company.contact
        form.address1.data = company.address1
        form.address2.data = company.address2
        form.postcode.data = company.postcode
        form.city.data = company.city
        form.active.data = company.active
        form.notes.data = company.notes

        #load up company packages
        company_packages_get = db.session.execute(
                    sa.select(CompanyPackage)
                    .where(CompanyPackage.company_id == company.id)
                ).scalars().all()

    if form.validate_on_submit():
        package_id_list = request.form.getlist('package_id') #pull package_ids from request.form

        company_packages_get = db.session.execute(
                    sa.select(CompanyPackage)
                    .where(CompanyPackage.company_id == company.id)
                ).scalars().all()
        
        company_package_ids = [] #list of all current package_ids in company_package db
        for company_package in company_packages_get:
            company_package_ids.append(company_package.package_id)

        try:
            company.name = form.name.data
            company.contact = form.contact.data
            company.address1 = form.address1.data
            company.address2 = form.address2.data
            company.postcode = form.postcode.data
            company.city = form.city.data
            company.active = form.active.data
            company.notes = form.notes.data

            package_price_list = [] #list of package prices from form
            for package in form.packages:
                package_price_list.append(package.price.data)
        
            #create id / price dict
            id_price_dict = []
            i = 0
            for package in package_id_list:
                id_price_dict.append({"id": package, "price": package_price_list[i]})
                i += 1
            
            #loop through dict to update package prices
            for i in id_price_dict:
                #if package id already exists in company_packages
                if int(i["id"]) in company_package_ids:
                    for company_package in company_packages_get:
                        if int(company_package.package_id) == int(i["id"]):
                            company_package.price = i["price"]
                            db.session.commit()
                            continue
                #if package id does not exist in company_package (new package type)
                else:
                    new_company_package = CompanyPackage(
                        company_id = company.id,
                        package_id = i["id"],
                        price = i["price"]
                    )
                    db.session.add(new_company_package)
          
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

@app.route("/companies/<company_name>/assignees")
@login_required
def company_assignees(company_name):
    #assignees = db.session.execute(sa.select(Assignee).where(Company.name == company_name)).scalars().all()
    company = db.session.execute(sa.select(Company).where(Company.name == company_name)).scalar_one_or_none()

    if company is None:
        #handle the case where company does not exist
        return render_template("404.html", message="Company not found"),404
    
    assignees = company.assignees

    return render_template("view_company_assignees.html", title=f"{company_name} - Assignees", assignees=assignees, company_name=company_name)

@app.route("/inactive_companies", methods=["GET"])
@login_required
def view_inactive_companies():
    inactive_companies = db.session.execute(
        sa.select(Company)
        .where(Company.active == False)
    ).scalars().all()

    return render_template("view_companies_inactive.html", title="Inactive Companies", inactive_companies=inactive_companies)