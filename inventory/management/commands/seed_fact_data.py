import random
import datetime
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from inventory.models import Reagent, StockTransaction
from equipment.models import Equipment, MaintenanceLog

User = get_user_model()

class Command(BaseCommand):
    help = 'Seeds StockTransactions and MaintenanceLogs for existing Reagents and Equipment'

    def handle(self, *args, **options):
        self.stdout.write("Checking for users...")
        users = list(User.objects.all())
        staff_users = [u for u in users if u.role not in [User.ROLE_PATIENT, User.ROLE_DOCTOR]] or users
        admin_user = staff_users[0] if staff_users else None

        if not admin_user:
            self.stdout.write(self.style.ERROR("No users found in database. Run seed_data first."))
            return

        reagents = list(Reagent.objects.all())
        equipments = list(Equipment.objects.all())

        if not reagents:
            self.stdout.write(self.style.ERROR("No reagents found in database to seed stock transactions."))
        else:
            self.stdout.write(f"Found {len(reagents)} reagents. Generating stock transactions...")
            
            # Date range: April 1, 2026 to July 28, 2026
            start_date = datetime.date(2026, 4, 1)
            end_date = datetime.date(2026, 7, 28)
            delta_days = (end_date - start_date).days

            tx_count = 0
            for rgt in reagents:
                # generate 5-15 transactions for each reagent
                num_tx = random.randint(5, 15)
                for _ in range(num_tx):
                    tx_type = random.choice([StockTransaction.TYPE_RECEIVE, StockTransaction.TYPE_ISSUE, StockTransaction.TYPE_ADJUST])
                    
                    # Ensure quantity doesn't drive stock negative if issuing
                    if tx_type == StockTransaction.TYPE_ISSUE:
                        current_stock = Decimal(str(rgt.current_quantity))
                        if current_stock > 1:
                            qty = Decimal(f"{random.uniform(0.1, float(current_stock) * 0.8):.2f}")
                        else:
                            tx_type = StockTransaction.TYPE_RECEIVE
                            qty = Decimal(f"{random.uniform(10.0, 100.0):.2f}")
                    else:
                        qty = Decimal(f"{random.uniform(1.0, 50.0):.2f}")
                    
                    random_days = random.randint(0, delta_days)
                    random_date = start_date + datetime.timedelta(days=random_days)
                    tx_time = datetime.datetime.combine(
                        random_date,
                        datetime.time(random.randint(0, 23), random.randint(0, 59), random.randint(0, 59))
                    )
                    tx_datetime = timezone.make_aware(tx_time)

                    ref_num = f"REF-INV-{random.randint(100000, 999999)}"
                    staff = random.choice(staff_users)

                    tx = StockTransaction.objects.create(
                        reagent=rgt,
                        transaction_type=tx_type,
                        quantity=qty,
                        reference_number=ref_num,
                        notes=f"Seeded transaction for testing ({tx_type})",
                        created_by=staff,
                        updated_by=staff
                    )
                    tx.created_at = tx_datetime
                    tx.save()
                    StockTransaction.objects.filter(id=tx.id).update(created_at=tx_datetime)
                    tx_count += 1

            self.stdout.write(self.style.SUCCESS(f"Successfully generated {tx_count} stock transactions!"))

        if not equipments:
            self.stdout.write(self.style.ERROR("No equipment found in database to seed maintenance logs."))
        else:
            self.stdout.write(f"Found {len(equipments)} equipment. Generating maintenance logs...")
            
            start_date = datetime.date(2026, 4, 1)
            end_date = datetime.date(2026, 7, 28)
            delta_days = (end_date - start_date).days

            log_count = 0
            engineers = [
                "Eng. Samuel Owusu", "Eng. Derek Asante", "Eng. Michael Appiah", 
                "Global Biotech Support", "Sysmex Technical Team", "Roche Field Support"
            ]

            for eq in equipments:
                # generate 3-8 maintenance logs for each equipment
                num_logs = random.randint(3, 8)
                for _ in range(num_logs):
                    m_type = random.choice([MaintenanceLog.TYPE_CALIBRATION, MaintenanceLog.TYPE_PREVENTIVE, MaintenanceLog.TYPE_REPAIR])
                    cost = Decimal(f"{random.uniform(50.0, 1200.0):.2f}")
                    
                    random_days = random.randint(0, delta_days)
                    random_date = start_date + datetime.timedelta(days=random_days)
                    start_time = datetime.datetime.combine(
                        random_date,
                        datetime.time(random.randint(0, 18), random.randint(0, 59), random.randint(0, 59))
                    )
                    start_datetime = timezone.make_aware(start_time)
                    
                    # duration 1 to 5 hours
                    end_datetime = start_datetime + datetime.timedelta(hours=random.randint(1, 5))
                    staff = random.choice(staff_users)

                    log = MaintenanceLog.objects.create(
                        equipment=eq,
                        maintenance_type=m_type,
                        performed_by_name=random.choice(engineers),
                        notes=f"Scheduled {m_type} run. Calibration and component testing verified.",
                        cost=cost,
                        start_date=start_datetime,
                        end_date=end_datetime,
                        created_by=staff,
                        updated_by=staff
                    )
                    log.created_at = start_datetime
                    log.save()
                    MaintenanceLog.objects.filter(id=log.id).update(created_at=start_datetime)
                    log_count += 1

            self.stdout.write(self.style.SUCCESS(f"Successfully generated {log_count} maintenance logs!"))
