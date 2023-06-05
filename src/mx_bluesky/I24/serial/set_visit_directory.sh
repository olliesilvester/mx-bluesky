visit=$1

ex_pv=BL24I-EA-IOC-12:GP1
ft_pv=ME14E-MO-IOC-01:GP100

caput  $ex_pv $visit
caput  $ft_pv $visit

echo "Visit set to: $visit"