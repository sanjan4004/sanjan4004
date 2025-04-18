# Generated by Django 5.1.6 on 2025-04-05 16:43

import django.db.models.deletion
from decimal import Decimal
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AdminWallet',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('wallet_address', models.CharField(blank=True, max_length=255, null=True)),
                ('network', models.CharField(default='USDT-TRC20', max_length=50)),
                ('balance', models.DecimalField(decimal_places=8, default=0, max_digits=20)),
                ('admin', models.OneToOneField(limit_choices_to={'is_superuser': True}, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ExchangeRate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('base_currency', models.CharField(max_length=10)),
                ('target_currency', models.CharField(max_length=10)),
                ('rate', models.DecimalField(decimal_places=6, max_digits=12)),
                ('last_updated', models.DateTimeField(auto_now=True)),
            ],
            options={
                'unique_together': {('base_currency', 'target_currency')},
            },
        ),
        migrations.CreateModel(
            name='KYCVerification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('id_type', models.CharField(choices=[('Passport', 'Passport'), ('National ID', 'National ID'), ('Driver License', 'Driver License')], max_length=50)),
                ('id_number', models.CharField(max_length=50)),
                ('verified', models.BooleanField(default=False)),
                ('id_image', models.ImageField(upload_to='kyc/')),
                ('selfie_image', models.ImageField(upload_to='kyc/selfies/')),
                ('status', models.CharField(choices=[('Pending', 'Pending'), ('Approved', 'Approved'), ('Rejected', 'Rejected')], default='Pending', max_length=20)),
                ('submitted_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Recipient',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('full_name', models.CharField(max_length=100)),
                ('country', models.CharField(choices=[('ABW', 'Aruba'), ('AFG', 'Afghanistan'), ('AGO', 'Angola'), ('AIA', 'Anguilla'), ('ALA', 'Åland Islands'), ('ALB', 'Albania'), ('AND', 'Andorra'), ('ARE', 'United Arab Emirates'), ('ARG', 'Argentina'), ('ARM', 'Armenia'), ('ASM', 'American Samoa'), ('ATA', 'Antarctica'), ('ATF', 'French Southern and Antarctic Lands'), ('ATG', 'Antigua and Barbuda'), ('AUS', 'Australia'), ('AUT', 'Austria'), ('AZE', 'Azerbaijan'), ('BDI', 'Burundi'), ('BEL', 'Belgium'), ('BEN', 'Benin'), ('BES', 'Caribbean Netherlands'), ('BFA', 'Burkina Faso'), ('BGD', 'Bangladesh'), ('BGR', 'Bulgaria'), ('BHR', 'Bahrain'), ('BHS', 'Bahamas'), ('BIH', 'Bosnia and Herzegovina'), ('BLM', 'Saint Barthélemy'), ('BLR', 'Belarus'), ('BLZ', 'Belize'), ('BMU', 'Bermuda'), ('BOL', 'Bolivia'), ('BRA', 'Brazil'), ('BRB', 'Barbados'), ('BRN', 'Brunei'), ('BTN', 'Bhutan'), ('BVT', 'Bouvet Island'), ('BWA', 'Botswana'), ('CAF', 'Central African Republic'), ('CAN', 'Canada'), ('CCK', 'Cocos (Keeling) Islands'), ('CHE', 'Switzerland'), ('CHL', 'Chile'), ('CHN', 'China'), ('CIV', 'Ivory Coast'), ('CMR', 'Cameroon'), ('COD', 'DR Congo'), ('COG', 'Republic of the Congo'), ('COK', 'Cook Islands'), ('COL', 'Colombia'), ('COM', 'Comoros'), ('CPV', 'Cape Verde'), ('CRI', 'Costa Rica'), ('CUB', 'Cuba'), ('CUW', 'Curaçao'), ('CXR', 'Christmas Island'), ('CYM', 'Cayman Islands'), ('CYP', 'Cyprus'), ('CZE', 'Czechia'), ('DEU', 'Germany'), ('DJI', 'Djibouti'), ('DMA', 'Dominica'), ('DNK', 'Denmark'), ('DOM', 'Dominican Republic'), ('DZA', 'Algeria'), ('ECU', 'Ecuador'), ('EGY', 'Egypt'), ('ERI', 'Eritrea'), ('ESH', 'Western Sahara'), ('ESP', 'Spain'), ('EST', 'Estonia'), ('ETH', 'Ethiopia'), ('FIN', 'Finland'), ('FJI', 'Fiji'), ('FLK', 'Falkland Islands'), ('FRA', 'France'), ('FRO', 'Faroe Islands'), ('FSM', 'Micronesia'), ('GAB', 'Gabon'), ('GBR', 'United Kingdom'), ('GEO', 'Georgia'), ('GGY', 'Guernsey'), ('GHA', 'Ghana'), ('GIB', 'Gibraltar'), ('GIN', 'Guinea'), ('GLP', 'Guadeloupe'), ('GMB', 'Gambia'), ('GNB', 'Guinea-Bissau'), ('GNQ', 'Equatorial Guinea'), ('GRC', 'Greece'), ('GRD', 'Grenada'), ('GRL', 'Greenland'), ('GTM', 'Guatemala'), ('GUF', 'French Guiana'), ('GUM', 'Guam'), ('GUY', 'Guyana'), ('HKG', 'Hong Kong'), ('HMD', 'Heard Island and McDonald Islands'), ('HND', 'Honduras'), ('HRV', 'Croatia'), ('HTI', 'Haiti'), ('HUN', 'Hungary'), ('IDN', 'Indonesia'), ('IMN', 'Isle of Man'), ('IND', 'India'), ('IOT', 'British Indian Ocean Territory'), ('IRL', 'Ireland'), ('IRN', 'Iran'), ('IRQ', 'Iraq'), ('ISL', 'Iceland'), ('ISR', 'Israel'), ('ITA', 'Italy'), ('JAM', 'Jamaica'), ('JEY', 'Jersey'), ('JOR', 'Jordan'), ('JPN', 'Japan'), ('KAZ', 'Kazakhstan'), ('KEN', 'Kenya'), ('KGZ', 'Kyrgyzstan'), ('KHM', 'Cambodia'), ('KIR', 'Kiribati'), ('KNA', 'Saint Kitts and Nevis'), ('KOR', 'South Korea'), ('KWT', 'Kuwait'), ('LAO', 'Laos'), ('LBN', 'Lebanon'), ('LBR', 'Liberia'), ('LBY', 'Libya'), ('LCA', 'Saint Lucia'), ('LIE', 'Liechtenstein'), ('LKA', 'Sri Lanka'), ('LSO', 'Lesotho'), ('LTU', 'Lithuania'), ('LUX', 'Luxembourg'), ('LVA', 'Latvia'), ('MAC', 'Macau'), ('MAF', 'Saint Martin'), ('MAR', 'Morocco'), ('MCO', 'Monaco'), ('MDA', 'Moldova'), ('MDG', 'Madagascar'), ('MDV', 'Maldives'), ('MEX', 'Mexico'), ('MHL', 'Marshall Islands'), ('MKD', 'North Macedonia'), ('MLI', 'Mali'), ('MLT', 'Malta'), ('MMR', 'Myanmar'), ('MNE', 'Montenegro'), ('MNG', 'Mongolia'), ('MNP', 'Northern Mariana Islands'), ('MOZ', 'Mozambique'), ('MRT', 'Mauritania'), ('MSR', 'Montserrat'), ('MTQ', 'Martinique'), ('MUS', 'Mauritius'), ('MWI', 'Malawi'), ('MYS', 'Malaysia'), ('MYT', 'Mayotte'), ('NAM', 'Namibia'), ('NCL', 'New Caledonia'), ('NER', 'Niger'), ('NFK', 'Norfolk Island'), ('NGA', 'Nigeria'), ('NIC', 'Nicaragua'), ('NIU', 'Niue'), ('NLD', 'Netherlands'), ('NOR', 'Norway'), ('NPL', 'Nepal'), ('NRU', 'Nauru'), ('NZL', 'New Zealand'), ('OMN', 'Oman'), ('PAK', 'Pakistan'), ('PAN', 'Panama'), ('PCN', 'Pitcairn Islands'), ('PER', 'Peru'), ('PHL', 'Philippines'), ('PLW', 'Palau'), ('PNG', 'Papua New Guinea'), ('POL', 'Poland'), ('PRI', 'Puerto Rico'), ('PRK', 'North Korea'), ('PRT', 'Portugal'), ('PRY', 'Paraguay'), ('PSE', 'Palestine'), ('PYF', 'French Polynesia'), ('QAT', 'Qatar'), ('REU', 'Réunion'), ('ROU', 'Romania'), ('RUS', 'Russia'), ('RWA', 'Rwanda'), ('SAU', 'Saudi Arabia'), ('SDN', 'Sudan'), ('SEN', 'Senegal'), ('SGP', 'Singapore'), ('SGS', 'South Georgia'), ('SHN', 'Saint Helena, Ascension and Tristan da Cunha'), ('SJM', 'Svalbard and Jan Mayen'), ('SLB', 'Solomon Islands'), ('SLE', 'Sierra Leone'), ('SLV', 'El Salvador'), ('SMR', 'San Marino'), ('SOM', 'Somalia'), ('SPM', 'Saint Pierre and Miquelon'), ('SRB', 'Serbia'), ('SSD', 'South Sudan'), ('STP', 'São Tomé and Príncipe'), ('SUR', 'Suriname'), ('SVK', 'Slovakia'), ('SVN', 'Slovenia'), ('SWE', 'Sweden'), ('SWZ', 'Eswatini'), ('SXM', 'Sint Maarten'), ('SYC', 'Seychelles'), ('SYR', 'Syria'), ('TCA', 'Turks and Caicos Islands'), ('TCD', 'Chad'), ('TGO', 'Togo'), ('THA', 'Thailand'), ('TJK', 'Tajikistan'), ('TKL', 'Tokelau'), ('TKM', 'Turkmenistan'), ('TLS', 'Timor-Leste'), ('TON', 'Tonga'), ('TTO', 'Trinidad and Tobago'), ('TUN', 'Tunisia'), ('TUR', 'Turkey'), ('TUV', 'Tuvalu'), ('TWN', 'Taiwan'), ('TZA', 'Tanzania'), ('UGA', 'Uganda'), ('UKR', 'Ukraine'), ('UMI', 'United States Minor Outlying Islands'), ('UNK', 'Kosovo'), ('URY', 'Uruguay'), ('USA', 'United States'), ('UZB', 'Uzbekistan'), ('VAT', 'Vatican City'), ('VCT', 'Saint Vincent and the Grenadines'), ('VEN', 'Venezuela'), ('VGB', 'British Virgin Islands'), ('VIR', 'United States Virgin Islands'), ('VNM', 'Vietnam'), ('VUT', 'Vanuatu'), ('WLF', 'Wallis and Futuna'), ('WSM', 'Samoa'), ('YEM', 'Yemen'), ('ZAF', 'South Africa'), ('ZMB', 'Zambia'), ('ZWE', 'Zimbabwe')], max_length=5)),
                ('currency', models.CharField(choices=[('USD', 'US Dollar'), ('EUR', 'Euro'), ('GBP', 'British Pound'), ('KES', 'Kenyan Shilling'), ('NGN', 'Nigerian Naira'), ('BTC', 'Bitcoin'), ('ETH', 'Ethereum'), ('JCB', 'Japan Credit Bureau'), ('USDT', 'United States Tether'), ('BNB', 'Binance Coin')], default=' GBP', max_length=10)),
                ('mobile_wallet', models.CharField(blank=True, max_length=50, null=True)),
                ('bank_account', models.CharField(blank=True, max_length=50, null=True)),
                ('payment_method', models.CharField(choices=[('GPay', 'Google Pay'), ('APay', 'Apple Pay'), ('Crypto', 'Cryptocurrency'), ('Bank Transfer', 'Bank Transfer'), ('M-Pesa', 'M-Pesa'), ('Binance', 'Binance'), ('Mobile Wallet', 'Mobile Wallet'), ('Card', 'Card')], max_length=50)),
                ('phone_number', models.CharField(blank=True, max_length=15, null=True)),
                ('binance_pay_id', models.CharField(blank=True, max_length=100, null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('country', models.CharField(choices=[('ABW', 'Aruba'), ('AFG', 'Afghanistan'), ('AGO', 'Angola'), ('AIA', 'Anguilla'), ('ALA', 'Åland Islands'), ('ALB', 'Albania'), ('AND', 'Andorra'), ('ARE', 'United Arab Emirates'), ('ARG', 'Argentina'), ('ARM', 'Armenia'), ('ASM', 'American Samoa'), ('ATA', 'Antarctica'), ('ATF', 'French Southern and Antarctic Lands'), ('ATG', 'Antigua and Barbuda'), ('AUS', 'Australia'), ('AUT', 'Austria'), ('AZE', 'Azerbaijan'), ('BDI', 'Burundi'), ('BEL', 'Belgium'), ('BEN', 'Benin'), ('BES', 'Caribbean Netherlands'), ('BFA', 'Burkina Faso'), ('BGD', 'Bangladesh'), ('BGR', 'Bulgaria'), ('BHR', 'Bahrain'), ('BHS', 'Bahamas'), ('BIH', 'Bosnia and Herzegovina'), ('BLM', 'Saint Barthélemy'), ('BLR', 'Belarus'), ('BLZ', 'Belize'), ('BMU', 'Bermuda'), ('BOL', 'Bolivia'), ('BRA', 'Brazil'), ('BRB', 'Barbados'), ('BRN', 'Brunei'), ('BTN', 'Bhutan'), ('BVT', 'Bouvet Island'), ('BWA', 'Botswana'), ('CAF', 'Central African Republic'), ('CAN', 'Canada'), ('CCK', 'Cocos (Keeling) Islands'), ('CHE', 'Switzerland'), ('CHL', 'Chile'), ('CHN', 'China'), ('CIV', 'Ivory Coast'), ('CMR', 'Cameroon'), ('COD', 'DR Congo'), ('COG', 'Republic of the Congo'), ('COK', 'Cook Islands'), ('COL', 'Colombia'), ('COM', 'Comoros'), ('CPV', 'Cape Verde'), ('CRI', 'Costa Rica'), ('CUB', 'Cuba'), ('CUW', 'Curaçao'), ('CXR', 'Christmas Island'), ('CYM', 'Cayman Islands'), ('CYP', 'Cyprus'), ('CZE', 'Czechia'), ('DEU', 'Germany'), ('DJI', 'Djibouti'), ('DMA', 'Dominica'), ('DNK', 'Denmark'), ('DOM', 'Dominican Republic'), ('DZA', 'Algeria'), ('ECU', 'Ecuador'), ('EGY', 'Egypt'), ('ERI', 'Eritrea'), ('ESH', 'Western Sahara'), ('ESP', 'Spain'), ('EST', 'Estonia'), ('ETH', 'Ethiopia'), ('FIN', 'Finland'), ('FJI', 'Fiji'), ('FLK', 'Falkland Islands'), ('FRA', 'France'), ('FRO', 'Faroe Islands'), ('FSM', 'Micronesia'), ('GAB', 'Gabon'), ('GBR', 'United Kingdom'), ('GEO', 'Georgia'), ('GGY', 'Guernsey'), ('GHA', 'Ghana'), ('GIB', 'Gibraltar'), ('GIN', 'Guinea'), ('GLP', 'Guadeloupe'), ('GMB', 'Gambia'), ('GNB', 'Guinea-Bissau'), ('GNQ', 'Equatorial Guinea'), ('GRC', 'Greece'), ('GRD', 'Grenada'), ('GRL', 'Greenland'), ('GTM', 'Guatemala'), ('GUF', 'French Guiana'), ('GUM', 'Guam'), ('GUY', 'Guyana'), ('HKG', 'Hong Kong'), ('HMD', 'Heard Island and McDonald Islands'), ('HND', 'Honduras'), ('HRV', 'Croatia'), ('HTI', 'Haiti'), ('HUN', 'Hungary'), ('IDN', 'Indonesia'), ('IMN', 'Isle of Man'), ('IND', 'India'), ('IOT', 'British Indian Ocean Territory'), ('IRL', 'Ireland'), ('IRN', 'Iran'), ('IRQ', 'Iraq'), ('ISL', 'Iceland'), ('ISR', 'Israel'), ('ITA', 'Italy'), ('JAM', 'Jamaica'), ('JEY', 'Jersey'), ('JOR', 'Jordan'), ('JPN', 'Japan'), ('KAZ', 'Kazakhstan'), ('KEN', 'Kenya'), ('KGZ', 'Kyrgyzstan'), ('KHM', 'Cambodia'), ('KIR', 'Kiribati'), ('KNA', 'Saint Kitts and Nevis'), ('KOR', 'South Korea'), ('KWT', 'Kuwait'), ('LAO', 'Laos'), ('LBN', 'Lebanon'), ('LBR', 'Liberia'), ('LBY', 'Libya'), ('LCA', 'Saint Lucia'), ('LIE', 'Liechtenstein'), ('LKA', 'Sri Lanka'), ('LSO', 'Lesotho'), ('LTU', 'Lithuania'), ('LUX', 'Luxembourg'), ('LVA', 'Latvia'), ('MAC', 'Macau'), ('MAF', 'Saint Martin'), ('MAR', 'Morocco'), ('MCO', 'Monaco'), ('MDA', 'Moldova'), ('MDG', 'Madagascar'), ('MDV', 'Maldives'), ('MEX', 'Mexico'), ('MHL', 'Marshall Islands'), ('MKD', 'North Macedonia'), ('MLI', 'Mali'), ('MLT', 'Malta'), ('MMR', 'Myanmar'), ('MNE', 'Montenegro'), ('MNG', 'Mongolia'), ('MNP', 'Northern Mariana Islands'), ('MOZ', 'Mozambique'), ('MRT', 'Mauritania'), ('MSR', 'Montserrat'), ('MTQ', 'Martinique'), ('MUS', 'Mauritius'), ('MWI', 'Malawi'), ('MYS', 'Malaysia'), ('MYT', 'Mayotte'), ('NAM', 'Namibia'), ('NCL', 'New Caledonia'), ('NER', 'Niger'), ('NFK', 'Norfolk Island'), ('NGA', 'Nigeria'), ('NIC', 'Nicaragua'), ('NIU', 'Niue'), ('NLD', 'Netherlands'), ('NOR', 'Norway'), ('NPL', 'Nepal'), ('NRU', 'Nauru'), ('NZL', 'New Zealand'), ('OMN', 'Oman'), ('PAK', 'Pakistan'), ('PAN', 'Panama'), ('PCN', 'Pitcairn Islands'), ('PER', 'Peru'), ('PHL', 'Philippines'), ('PLW', 'Palau'), ('PNG', 'Papua New Guinea'), ('POL', 'Poland'), ('PRI', 'Puerto Rico'), ('PRK', 'North Korea'), ('PRT', 'Portugal'), ('PRY', 'Paraguay'), ('PSE', 'Palestine'), ('PYF', 'French Polynesia'), ('QAT', 'Qatar'), ('REU', 'Réunion'), ('ROU', 'Romania'), ('RUS', 'Russia'), ('RWA', 'Rwanda'), ('SAU', 'Saudi Arabia'), ('SDN', 'Sudan'), ('SEN', 'Senegal'), ('SGP', 'Singapore'), ('SGS', 'South Georgia'), ('SHN', 'Saint Helena, Ascension and Tristan da Cunha'), ('SJM', 'Svalbard and Jan Mayen'), ('SLB', 'Solomon Islands'), ('SLE', 'Sierra Leone'), ('SLV', 'El Salvador'), ('SMR', 'San Marino'), ('SOM', 'Somalia'), ('SPM', 'Saint Pierre and Miquelon'), ('SRB', 'Serbia'), ('SSD', 'South Sudan'), ('STP', 'São Tomé and Príncipe'), ('SUR', 'Suriname'), ('SVK', 'Slovakia'), ('SVN', 'Slovenia'), ('SWE', 'Sweden'), ('SWZ', 'Eswatini'), ('SXM', 'Sint Maarten'), ('SYC', 'Seychelles'), ('SYR', 'Syria'), ('TCA', 'Turks and Caicos Islands'), ('TCD', 'Chad'), ('TGO', 'Togo'), ('THA', 'Thailand'), ('TJK', 'Tajikistan'), ('TKL', 'Tokelau'), ('TKM', 'Turkmenistan'), ('TLS', 'Timor-Leste'), ('TON', 'Tonga'), ('TTO', 'Trinidad and Tobago'), ('TUN', 'Tunisia'), ('TUR', 'Turkey'), ('TUV', 'Tuvalu'), ('TWN', 'Taiwan'), ('TZA', 'Tanzania'), ('UGA', 'Uganda'), ('UKR', 'Ukraine'), ('UMI', 'United States Minor Outlying Islands'), ('UNK', 'Kosovo'), ('URY', 'Uruguay'), ('USA', 'United States'), ('UZB', 'Uzbekistan'), ('VAT', 'Vatican City'), ('VCT', 'Saint Vincent and the Grenadines'), ('VEN', 'Venezuela'), ('VGB', 'British Virgin Islands'), ('VIR', 'United States Virgin Islands'), ('VNM', 'Vietnam'), ('VUT', 'Vanuatu'), ('WLF', 'Wallis and Futuna'), ('WSM', 'Samoa'), ('YEM', 'Yemen'), ('ZAF', 'South Africa'), ('ZMB', 'Zambia'), ('ZWE', 'Zimbabwe')], default='KEN', max_length=5)),
                ('currency', models.CharField(choices=[('USD', 'US Dollar'), ('EUR', 'Euro'), ('GBP', 'British Pound'), ('KES', 'Kenyan Shilling'), ('NGN', 'Nigerian Naira'), ('BTC', 'Bitcoin'), ('ETH', 'Ethereum'), ('JCB', 'Japan Credit Bureau'), ('USDT', 'United States Tether'), ('BNB', 'Binance Coin')], default='GBP', max_length=5)),
                ('exchange_rate', models.DecimalField(decimal_places=4, default=Decimal('1.0'), max_digits=10)),
                ('transaction_fee', models.DecimalField(decimal_places=2, default=Decimal('3.00'), max_digits=10)),
                ('total_amount', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=10)),
                ('payment_method', models.CharField(choices=[('GPay', 'Google Pay'), ('APay', 'Apple Pay'), ('Crypto', 'Cryptocurrency'), ('Bank Transfer', 'Bank Transfer'), ('M-Pesa', 'M-Pesa'), ('Binance', 'Binance'), ('Mobile Wallet', 'Mobile Wallet'), ('Card', 'Card')], max_length=50)),
                ('status', models.CharField(choices=[('Pending', 'Pending'), ('Processing', 'Processing'), ('Completed', 'Completed'), ('Failed', 'Failed'), ('Refunded', 'Refunded')], default='Pending', max_length=20)),
                ('transaction_reference', models.CharField(max_length=255, unique=True)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('fee_transferred', models.BooleanField(default=False)),
                ('fee_status', models.CharField(choices=[('Pending', 'Pending'), ('Transferred', 'Transferred'), ('Failed', 'Failed')], default='Pending', max_length=20)),
                ('crypto_type', models.CharField(blank=True, choices=[('BTC', 'Bitcoin'), ('ETH', 'Ethereum'), ('USDT', 'Tether'), ('BNB', 'Binance Coin'), ('XRP', 'XRP')], max_length=50, null=True)),
                ('crypto_address', models.CharField(blank=True, max_length=255, null=True)),
                ('mpesa_phone_number', models.CharField(blank=True, max_length=15, null=True)),
                ('card_number', models.CharField(blank=True, max_length=16, null=True)),
                ('expiry_date', models.CharField(blank=True, max_length=5, null=True)),
                ('cvv', models.CharField(blank=True, max_length=4, null=True)),
                ('payment_token', models.CharField(blank=True, max_length=100, null=True)),
                ('account_number', models.CharField(blank=True, max_length=20, null=True)),
                ('bank_name', models.CharField(blank=True, max_length=100, null=True)),
                ('admin_wallet', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='WorldTtance.adminwallet')),
                ('recipient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='WorldTtance.recipient')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phone_number', models.CharField(blank=True, max_length=15, null=True)),
                ('address', models.CharField(blank=True, max_length=200, null=True)),
                ('country', models.CharField(blank=True, max_length=50, null=True)),
                ('date_of_birth', models.DateField(blank=True, null=True)),
                ('profile_picture', models.ImageField(blank=True, null=True, upload_to='profile_pics/')),
                ('kyc_verified', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
