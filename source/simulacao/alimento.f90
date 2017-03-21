module alimento

contains

subroutine evolui_tempo(tf, T_inicial, Raio, H, ka, rho, Cp, h_convec, eps, T_esteira, T_paredes, T_ar, T_ambiente,T)

    implicit none
    integer, parameter :: nr = 60
    integer, parameter :: nh = 30
    real, dimension(nh,nr), intent(in) :: T_inicial
    real, intent(in) :: tf, Raio, H, ka, rho, Cp, h_convec, eps
    real, intent(in) :: T_esteira, T_paredes, T_ar, T_ambiente
    real, dimension(nh,nr), intent(out) :: T
    real:: sigma, alpha, dr, dh, dt
    integer :: nt, i, j, k, l, m
    REAL, PARAMETER :: pi = 3.1415927

    real, dimension(nr) :: r
    real, dimension(nh,nr) :: Tc

    dt = 0.05
    sigma = 5.67032e-8
    alpha = ka/(rho*Cp)
    dr = Raio/(nr + 1)
    dh = H/(nh + 1)
    nt = int(tf/dt)

    do i = 1, int(nh)
        do j = 1, int(nr)
            T(i,j) = T_inicial(i,j)
            Tc(i,j) = T_inicial(i,j)
        enddo
    enddo

    do i = 1, nr
        T(1,i) = T_esteira
        r(i) = i*Raio/nr
    enddo

    do k = 1, nt

        do i = 1, int(nh)
            do j = 1, int(nr)
                Tc(i,j) = T(i,j)
            enddo
        enddo

        do i = 2, int(nh) -1
            do j = 2, int(nr) -1
                T(i,j) = Tc(i,j) + dt*alpha*( &
                (  Tc(i,j+1) - 2*Tc(i,j) + T(i,j-1)  )/dr**2 + &
                ( Tc(i+1,j) - 2*Tc(i,j) + T(i-1,j)  )/dh**2 + &
                ( Tc(i,j+1) - Tc(i,j-1) )/(dr* r(j)) )
            enddo
        enddo

        do i = 1, int(nr)
            T(nh,i) = T(nh-1,i) + dr*eps*sigma*(T_paredes**4 - T(nh,i)**4)&
                      + dr*h_convec*( T_ar - T(nh,i))
        enddo

        do i = 1, int(nh)
            T(i,nr) = T(i,nr-1) + dr*eps*sigma*(T_paredes**4 - T(i,nr)**4)&
                      + dr*h_convec*( T_ar - T(i,nr))
        enddo

        do i = 1, int(nh)
            T(i,1) = T(i,2)
        enddo
    enddo

end subroutine evolui_tempo

end module alimento
