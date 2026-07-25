from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import ReferralPartner, Referral
from .serializers import ReferralPartnerSerializer, ReferralSerializer

class ReferralPartnerViewSet(viewsets.ModelViewSet):
    queryset = ReferralPartner.objects.all()
    serializer_class = ReferralPartnerSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, updated_by=self.request.user)

    @action(detail=True, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def ledger(self, request, pk=None):
        partner = self.get_object()
        referrals = partner.referrals.filter(is_deleted=False)
        
        # Incoming stats (commission to partner, discount applied)
        incoming = referrals.filter(referral_type='incoming')
        total_incoming_cases = incoming.count()
        total_commission = sum(r.commission_amount for r in incoming)
        paid_commission = sum(r.commission_amount for r in incoming.filter(payment_status='paid'))
        unpaid_commission = total_commission - paid_commission
        
        # Outgoing stats (cost to external lab)
        outgoing = referrals.filter(referral_type='outgoing')
        total_outgoing_cases = outgoing.count()
        total_cost = sum(r.amount for r in outgoing)
        paid_cost = sum(r.amount for r in outgoing.filter(payment_status='paid'))
        unpaid_cost = total_cost - paid_cost
        
        return Response({
            'partner_name': partner.name,
            'incoming': {
                'total_cases': total_incoming_cases,
                'total_commission': total_commission,
                'paid_commission': paid_commission,
                'unpaid_commission': unpaid_commission,
            },
            'outgoing': {
                'total_cases': total_outgoing_cases,
                'total_cost': total_cost,
                'paid_cost': paid_cost,
                'unpaid_cost': unpaid_cost,
            }
        })

class ReferralViewSet(viewsets.ModelViewSet):
    queryset = Referral.objects.all()
    serializer_class = ReferralSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, updated_by=self.request.user)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def mark_paid(self, request, pk=None):
        referral = self.get_object()
        from django.utils import timezone
        referral.payment_status = 'paid'
        referral.payment_date = timezone.now()
        referral.save()
        return Response({'status': 'Referral payment marked as paid.'})

