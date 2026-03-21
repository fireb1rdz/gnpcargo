from django.db import models, connection
from apps.core.models import TenantAwareModel
from apps.entities.models import Party

class PhysicalSpaceManager(models.Manager):
    def descendants_of(self, root_id, from_type=None):
        """
        Retorna IDs de todos os descendentes a partir de root_id.
        Se from_type for informado, retorna apenas espaços
        daquele tipo (e abaixo).
        """

        params = [root_id]

        type_filter_sql = ""
        if from_type:
            type_filter_sql = "AND ps.space_type = %s"
            params.append(from_type)

        with connection.cursor() as cursor:
            cursor.execute(f"""
                WITH RECURSIVE space_tree AS (
                    SELECT id, space_type
                    FROM warehouse_physicalspace
                    WHERE id = %s

                    UNION ALL

                    SELECT ps.id, ps.space_type
                    FROM warehouse_physicalspace ps
                    INNER JOIN space_tree st ON ps.parent_id = st.id
                )
                SELECT id
                FROM space_tree
                WHERE 1=1
                {type_filter_sql}
            """, params)

            return [row[0] for row in cursor.fetchall()]


class Codification(TenantAwareModel):
    codification = models.CharField(max_length=255)
    max_length = models.IntegerField()

class TrackingSequence(TenantAwareModel):
    current_value = models.BigIntegerField(default=0)

class Package(TenantAwareModel):
    STATUS_CHOICES = (
        ('generated', 'Generated'),
        ('activated', 'Activated'),
        ('stocked', 'Stocked'),
        ('pending', 'Pending'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    )
    created_by = models.ForeignKey(Party, related_name="created_packages", on_delete=models.PROTECT)
    holder = models.ForeignKey(Party, related_name="stored_packages", on_delete=models.PROTECT)
    tracking_code = models.CharField(max_length=120, db_index=True)
    product_description = models.CharField(max_length=500, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='generated')
    tracking_code_origin = models.CharField(
        choices=(('carrier', 'Carrier'), ('client', 'Client')),
        default='client'
    )
    length = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    width = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    height = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    weight = models.DecimalField(max_digits=10, decimal_places=3, default=0)

    @property
    def volume(self):
        return self.length * self.width * self.height

class PhysicalSpace(TenantAwareModel):
    holder = models.ForeignKey(Party, on_delete=models.PROTECT)
    SPACE_TYPE_CHOICES = (
        ("WAREHOUSE", "warehouse"),
        ("ZONE", "zone"),
        ("AISLE", "aisle"),
        ("RACK", "rack"),
        ("LEVEL", "level"),
        ("BIN", "bin"),
        ("FLOOR", "floor"),
        ("DOCK", "dock"),
        ("STAGING", "staging"),
    )

    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="children"
    )

    space_type = models.CharField(max_length=20, choices=SPACE_TYPE_CHOICES)
    code = models.CharField(max_length=50)

    max_volume = models.DecimalField(
        max_digits=14,
        decimal_places=3,
        null=True,
        blank=True
    )
    max_weight = models.DecimalField(
        max_digits=14,
        decimal_places=3,
        null=True,
        blank=True
    )

    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ("tenant", "parent", "code")
        indexes = [
            models.Index(fields=["tenant", "space_type"]),
        ]

    def __str__(self):
        return f"{self.space_type} - {self.code}"

class SpaceAllocation(TenantAwareModel):
    package = models.ForeignKey(
        Package,
        on_delete=models.CASCADE,
        related_name="allocations"
    )
    space = models.ForeignKey(
        PhysicalSpace,
        on_delete=models.PROTECT,
        related_name="allocations"
    )

    allocated_volume = models.DecimalField(
        max_digits=14,
        decimal_places=3
    )

    allocated_weight = models.DecimalField(
        max_digits=14,
        decimal_places=3
    )

    allocated_at = models.DateTimeField(auto_now_add=True)
    released_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["tenant", "space"]),
            models.Index(fields=["tenant", "package"]),
        ]

class SpaceCapacitySnapshot(TenantAwareModel):
    space = models.OneToOneField(
        PhysicalSpace,
        on_delete=models.CASCADE
    )
    used_volume = models.DecimalField(max_digits=14, decimal_places=3, default=0)
    used_weight = models.DecimalField(max_digits=14, decimal_places=3, default=0)
    updated_at = models.DateTimeField(auto_now=True)
