package com.stowage.system;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.stowage.system.client.AlgorithmModels;
import com.stowage.system.client.AlgorithmServiceClient;
import com.stowage.system.entity.*;
import com.stowage.system.repository.*;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.http.MediaType;
import org.springframework.test.context.ActiveProfiles;
import org.springframework.test.web.servlet.MockMvc;

import java.time.LocalDateTime;
import java.util.List;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@SpringBootTest
@AutoConfigureMockMvc
@ActiveProfiles("test")
class BackendIntegrationTest {

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private ObjectMapper objectMapper;

    @Autowired
    private ShipRepository shipRepository;

    @Autowired
    private HoldRepository holdRepository;

    @Autowired
    private ShipHydrostaticRepository hydrostaticRepository;

    @Autowired
    private CargoRepository cargoRepository;

    @Autowired
    private VoyageRepository voyageRepository;

    @Autowired
    private StowagePlanRepository planRepository;

    @Autowired
    private StowageItemRepository itemRepository;

    @Autowired
    private WarningRecordRepository warningRecordRepository;

    @MockBean
    private AlgorithmServiceClient algorithmServiceClient;

    @BeforeEach
    void setUp() {
        warningRecordRepository.deleteAll();
        itemRepository.deleteAll();
        planRepository.deleteAll();
        hydrostaticRepository.deleteAll();
        holdRepository.deleteAll();
        voyageRepository.deleteAll();
        cargoRepository.deleteAll();
        shipRepository.deleteAll();
    }

    @Test
    void shipCrudShouldWork() throws Exception {
        String request = """
            {
              "shipCode":"TEST-SHIP-001",
              "shipName":"Test Ship",
              "shipType":"GENERAL_CARGO",
              "lengthOverall":100.0,
              "lengthBetweenPerpendiculars":95.0,
              "beam":18.0,
              "depth":9.0,
              "lightshipWeight":1500.0,
              "lightshipKG":5.4,
              "lightshipLCG":46.0,
              "lightshipTCG":0.0,
              "designDisplacement":3600.0,
              "designGM":1.5,
              "remark":"test"
            }
            """;

        mockMvc.perform(post("/api/ships")
                .contentType(MediaType.APPLICATION_JSON)
                .content(request))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$.data.shipCode").value("TEST-SHIP-001"));

        Ship ship = shipRepository.findByShipCode("TEST-SHIP-001").orElseThrow();
        mockMvc.perform(get("/api/ships/" + ship.getId()))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$.data.shipName").value("Test Ship"));
    }

    @Test
    void cargoCrudShouldWork() throws Exception {
        String request = """
            {
              "cargoCode":"CG-T-001",
              "cargoName":"Test Cargo",
              "cargoCategory":"STEEL",
              "dangerousClass":null,
              "incompatibleTags":"",
              "isolationLevel":0.0,
              "weight":30.0,
              "length":6.0,
              "width":2.4,
              "height":2.2,
              "stackable":true,
              "rotatable":true,
              "centerOffsetX":0.0,
              "centerOffsetY":0.0,
              "centerOffsetZ":0.0,
              "remark":"test"
            }
            """;

        mockMvc.perform(post("/api/cargos")
                .contentType(MediaType.APPLICATION_JSON)
                .content(request))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$.data.cargoCode").value("CG-T-001"));
    }

    @Test
    void generatePlanEndpointShouldWork() throws Exception {
        SeedContext context = seedBaseData();
        when(algorithmServiceClient.generatePlan(any())).thenReturn(mockSolverResponse());

        String request = """
            {
              "cargoIds":[11],
              "config":{
                "gmMin":0.5,
                "adjacentHoldDiffMax":0.4,
                "ixMax":5000,
                "solverTimeLimitSeconds":10,
                "fsc":0.0,
                "defaultIsolationDistance":1.0,
                "maxIterations":3
              }
            }
            """;

        mockMvc.perform(post("/api/plans/" + context.plan().getId() + "/generate")
                .contentType(MediaType.APPLICATION_JSON)
                .content(request))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$.data.plan.planNo").value("PLAN-T-001"))
            .andExpect(jsonPath("$.data.plan.complianceStatus").value("PASS"))
            .andExpect(jsonPath("$.data.items[0].cargoId").value(11));
    }

    @Test
    void validatePlanEndpointShouldWork() throws Exception {
        SeedContext context = seedBaseData();
        StowageItem item = new StowageItem();
        item.setPlanId(context.plan().getId());
        item.setCargoId(context.cargo().getId());
        item.setHoldId(context.hold().getId());
        item.setLayerNo(1);
        item.setOrientation("LWH");
        item.setOriginX(0.0);
        item.setOriginY(0.0);
        item.setOriginZ(0.0);
        item.setPlacedLength(6.0);
        item.setPlacedWidth(2.4);
        item.setPlacedHeight(2.2);
        item.setCentroidX(3.0);
        item.setCentroidY(1.2);
        item.setCentroidZ(1.1);
        item.setStatus("PLACED");
        item.setViolationFlags("");
        itemRepository.save(item);

        when(algorithmServiceClient.validatePlan(any())).thenReturn(mockSolverResponse());

        String request = """
            {
              "config":{
                "gmMin":0.5,
                "adjacentHoldDiffMax":0.4,
                "ixMax":5000,
                "solverTimeLimitSeconds":10,
                "fsc":0.0,
                "defaultIsolationDistance":1.0,
                "maxIterations":3
              }
            }
            """;

        mockMvc.perform(post("/api/plans/" + context.plan().getId() + "/validate")
                .contentType(MediaType.APPLICATION_JSON)
                .content(request))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$.data.plan.gm").value(1.42))
            .andExpect(jsonPath("$.data.warnings").isArray());
    }

    private SeedContext seedBaseData() {
        Ship ship = new Ship();
        ship.setShipCode("GC-001");
        ship.setShipName("Harmony Trader");
        ship.setShipType("GENERAL_CARGO");
        ship.setLengthOverall(96.0);
        ship.setLengthBetweenPerpendiculars(90.0);
        ship.setBeam(16.8);
        ship.setDepth(9.2);
        ship.setLightshipWeight(1680.0);
        ship.setLightshipKG(5.5);
        ship.setLightshipLCG(47.0);
        ship.setLightshipTCG(0.0);
        ship.setDesignDisplacement(3650.0);
        ship.setDesignGM(1.6);
        ship = shipRepository.save(ship);

        Hold hold = new Hold();
        hold.setShipId(ship.getId());
        hold.setHoldNo("H1");
        hold.setLength(17.0);
        hold.setWidth(12.0);
        hold.setHeight(8.0);
        hold.setVolume(1632.0);
        hold.setLcg(19.0);
        hold.setTcg(0.0);
        hold.setVcg(5.0);
        hold.setMaxLoadWeight(420.0);
        hold.setDeckStrengthLimit(7.5);
        hold.setSequenceNo(1);
        hold = holdRepository.save(hold);

        ShipHydrostatic hydrostatic = new ShipHydrostatic();
        hydrostatic.setShipId(ship.getId());
        hydrostatic.setDisplacement(1900.0);
        hydrostatic.setKmValue(7.45);
        hydrostatic.setDraft(4.8);
        hydrostaticRepository.save(hydrostatic);

        Cargo cargo = new Cargo();
        cargo.setCargoCode("CG-001");
        cargo.setCargoName("Steel Coil");
        cargo.setCargoCategory("STEEL");
        cargo.setDangerousClass(null);
        cargo.setIncompatibleTags("");
        cargo.setIsolationLevel(0.0);
        cargo.setWeight(30.5);
        cargo.setLength(6.0);
        cargo.setWidth(2.4);
        cargo.setHeight(2.2);
        cargo.setStackable(true);
        cargo.setRotatable(true);
        cargo.setCenterOffsetX(0.0);
        cargo.setCenterOffsetY(0.0);
        cargo.setCenterOffsetZ(0.0);
        cargo = cargoRepository.save(cargo);

        Voyage voyage = new Voyage();
        voyage.setVoyageNo("VY-T-001");
        voyage.setShipId(ship.getId());
        voyage.setRouteInfo("Shanghai -> Busan");
        voyage.setDeparturePort("Shanghai");
        voyage.setArrivalPort("Busan");
        voyage.setEta(LocalDateTime.now().plusDays(2));
        voyage.setEtd(LocalDateTime.now().plusDays(1));
        voyage.setStatus("PLANNING");
        voyage = voyageRepository.save(voyage);

        StowagePlan plan = new StowagePlan();
        plan.setVoyageId(voyage.getId());
        plan.setPlanNo("PLAN-T-001");
        plan.setVersion(1);
        plan.setStatus("DRAFT");
        plan.setTotalCargoWeight(0.0);
        plan.setDisplacement(0.0);
        plan.setKg(0.0);
        plan.setLcg(0.0);
        plan.setTcg(0.0);
        plan.setGm(0.0);
        plan.setComplianceStatus("PENDING");
        plan.setWarningCount(0);
        plan = planRepository.save(plan);

        return new SeedContext(ship, hold, cargo, voyage, plan);
    }

    private AlgorithmModels.SolverResponse mockSolverResponse() {
        return new AlgorithmModels.SolverResponse(
            true,
            new AlgorithmModels.PlanSummaryPayload(
                1938.0,
                6.19,
                47.66,
                0.95,
                1.42,
                -0.18,
                857.65,
                "PASS",
                580.0,
                22.0,
                33.55,
                List.of(new AlgorithmModels.HoldSummaryPayload(1L, "H1", 30.5, 3.0, 1.2, 1.1, 0.02, 0.0187, 31.68)),
                List.of()
            ),
            List.of(
                new AlgorithmModels.SolverItemPayload(
                    11L, "CG-001", "Steel Coil", 1L, "H1", 1, "LWH",
                    0.0, 0.0, 0.0, 6.0, 2.4, 2.2, 3.0, 1.2, 1.1,
                    30.5, "STEEL", null, "PLACED", List.of()
                )
            ),
            List.of(),
            new AlgorithmModels.SolverMetricsPayload(120, 1, "FEASIBLE", List.of("mock")),
            List.of()
        );
    }

    private record SeedContext(Ship ship, Hold hold, Cargo cargo, Voyage voyage, StowagePlan plan) {
    }
}

