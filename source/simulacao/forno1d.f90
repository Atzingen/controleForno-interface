module perfil_forno

contains

subroutine calcula_perfil(Ta, T1, T2, T3, R1, R2, R3,T)
    implicit none

    real, intent(in) :: Ta, T1, T2, T3, R1, R2, R3
    integer, parameter :: n = 30   ! número de elementos finitos
    real, dimension(n), intent(out) :: T

    real :: L, sor, dx, T_media, Tn
    integer :: p_n1, p_n2, p_n3, i, j ,k
    real, dimension(n) :: fonte

    L = 1.5         ! comprimento do forno em metros
    sor = 1.85      ! parâmetro sor
    p_n1 = n/4      ! posição do primeiro sensor de Temperatura
    p_n2 = n/2      ! segundo sensor
    p_n3 = 3*n/4    ! terceiro sensor

    dx = L/(n+1)
    T_media = (2*Ta + T1 + T2 + T3)/5

    ! valores iniciais da temperatura
    do i=1, n-1
        T(i) = T_media
    enddo
    T(1) = Ta   ! tempa ambiente nas pontas (direichilet)
    T(n) = Ta   ! tempa ambiente nas pontas (direichilet)

    ! valores da fonte
    do i=1, INT(n/3)
        fonte(i) = R1
    enddo
    do i=INT(n/3)+1, INT(2*n/3)
        fonte(i) = R2
    enddo
    do i=INT(2*n/3)+1, n
        fonte(i) = R3
    enddo


    do j=1, 200
        do i=2 , n-1
            if (i == p_n1) then
                T(i) = T1
            else if (i == p_n2) then
                T(i) = T2
            else if (i == p_n3) then
                T(i) = T3
            else
                Tn = (T(i-1) + T(i+1))/2.0 +dx*dx*fonte(i)
                T(i) = T(i) + sor*( Tn - T(i) )
            end if
        enddo
    enddo

end subroutine calcula_perfil


end module perfil_forno
