from utilities.choices import ChoiceSet


class PlugTypeChoices(ChoiceSet):
    """Les types de configuration valides pour une prise."""
    TYPE_UPLINK = 'uplink'
    TYPE_STATIC = 'static'
    TYPE_DHCP = 'dhcp'
    TYPE_TRUNK = 'trunk'
    TYPE_AP = 'ap'

    CHOICES = (
        (TYPE_UPLINK, 'Uplink'),
        (TYPE_STATIC, 'Static'),
        (TYPE_DHCP, 'DHCP'),
        (TYPE_TRUNK, 'Trunk'),
        (TYPE_AP, 'Access Point'),
    )


class PlugStatusChoices(ChoiceSet):
    """Les statuts valides pour une prise."""
    STATUS_OPERATIONAL = 'operationnel'
    STATUS_TO_PATCH = 'a-patcher'
    STATUS_TO_CONFIGURE = 'a-configurer'
    STATUS_TO_DELETE = 'a-supprimer'
    STATUS_DELETED = 'supprimee'
    STATUS_VERIFY_PATCHING = 'verifier-patching'
    STATUS_VERIFY_FLUKE = 'verifier-fluke'
    STATUS_DEFECTIVE = 'defectueux'

    CHOICES = (
        (STATUS_OPERATIONAL, 'Opérationnel'),
        (STATUS_TO_PATCH, 'À patcher'),
        (STATUS_TO_CONFIGURE, 'À configurer'),
        (STATUS_TO_DELETE, 'À supprimer'),
        (STATUS_DELETED, 'Supprimée'),
        (STATUS_VERIFY_PATCHING, 'Vérifier patching'),
        (STATUS_VERIFY_FLUKE, 'Vérifier fluke'),
        (STATUS_DEFECTIVE, 'Défectueux'),
    )